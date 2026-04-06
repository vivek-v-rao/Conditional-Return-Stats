""" Pandas utilities """

import os
import numpy as np
import pandas as pd
from scipy import stats
import numpy.typing as npt
import param
from datetime import datetime
from typing import Tuple
from numpy_util import (count_non_nan, count_nonzero_non_nan,
    first_last_true_pos)
from stats import (annmean, vol, maxDD, cumul_div_maxDD, Sharpe, Sharpe_adj,
    meanabs)
profit_funcs = [annmean, vol, maxDD, cumul_div_maxDD, Sharpe, Sharpe_adj,
    stats.skew, stats.kurtosis, np.min, np.max]
func_renames = {"len":"#", "count_non_nan":"#obs", "amin":"min", "amax":"max",
    "cumul_div_maxDD":"cumul/maxDD", "count_nonzero_non_nan":"#nonzero"}
data_files_read = []

def min_max_indices_values(df):
    """
    Compute statistics for each column in the DataFrame, ignoring NaNs.
    Parameters:
    df (pd.DataFrame): Input DataFrame with numeric columns.
    Returns:
    pd.DataFrame: A DataFrame with the following statistics for each column:
        - #obs: Number of non-NaN observations.
        - min_index: Index of the minimum value.
        - max_index: Index of the maximum value.
        - min_value: Minimum value.
        - max_value: Maximum value.
        - median: Median value.
        - mean: Mean value.
        - std_dev: Standard deviation.
        - skew: Skew.
        - kurt: Kurtosis.
    """
    xstats = []
    for column in df.columns:
        col_data = df[column].dropna()
        if col_data.empty:
            xstats.append({
                '#obs': 0,
                'min_index': np.nan,
                'max_index': np.nan,
                'min_value': np.nan,
                'max_value': np.nan,
                'median': np.nan,
                'mean': np.nan,
                'std': np.nan,
                'skew': np.nan,
                'kurtosis': np.nan
            })
            continue
        num_obs = col_data.count()
        min_index = col_data.idxmin()
        max_index = col_data.idxmax()
        min_value = col_data.min()
        max_value = col_data.max()
        median = col_data.median()
        mean = col_data.mean()
        std_dev = col_data.std()
        xstats.append({
            '#obs': num_obs,
            'min_index': min_index,
            'max_index': max_index,
            'min_value': min_value,
            'max_value': max_value,
            'median': median,
            'mean': mean,
            'std': std_dev,
            'skew': stats.skew(col_data),
            'kurtosis': stats.kurtosis(col_data)
        })
    return pd.DataFrame(xstats, index=df.columns)

def tail_counts(df, x, tail="both", freq=True, freq_scale=1.0):
    """Count values in dataframe tails by threshold."""
    data = []
    index = []

    if tail == "right":
        for thresh in x:
            data.append(df.gt(thresh).sum(axis=0))
            index.append(f"> {thresh}")
    elif tail == "left":
        for thresh in x:
            data.append(df.le(-thresh).sum(axis=0))
            index.append(f"<= -{thresh}")
    elif tail == "both":
        for thresh in x:
            data.append(df.ge(thresh).sum(axis=0))
            index.append(f">= {thresh}")
            data.append(df.le(-thresh).sum(axis=0))
            index.append(f"<= -{thresh}")
    else:
        raise ValueError("tail must be 'right', 'left', or 'both'")

    df_count = pd.DataFrame(data, index=index, columns=df.columns)

    if not freq:
        return df_count

    denom = df.notna().sum(axis=0)
    df_freq = freq_scale * df_count.divide(denom.where(denom != 0), axis=1)

    out = pd.DataFrame(index=df_count.index)
    for col in df.columns:
        out[f"{col}_count"] = df_count[col]
        out[f"{col}_freq"] = df_freq[col]
    return out

def first_last_good_dates(df:pd.DataFrame, funcs=[np.mean, np.std, np.median,
    np.min, np.max], bad_value=np.nan) -> pd.DataFrame:
    """ return a dataframe with the first and last good dates of df by column,
    the # of good and bad observations, and other statistics in funcs """
    bad_date = datetime(1900,1,1).date()
    ncol = df.shape[1]
    ifirst, ilast = first_last_true_pos_by_column(df.notnull())
    df_out = pd.DataFrame(index=df.columns)
    df_out["first_index"] = np.where(ifirst >= 0, df.index[ifirst], bad_date)
    df_out["last_index"] = np.where(ilast  >= 0, df.index[ilast] , bad_date)
    df_out["pos_first"] = ifirst
    df_out["pos_last"]  = ilast
    df_out["len_range"] = df_out["pos_last"] - df_out["pos_first"] + 1
    df_out["#good"] = df.count(axis=0)
    df_out["#bad_in_range"] = df_out["len_range"] - df_out["#good"]
    df_out["frac_bad"] = df_out["#bad_in_range"] / df_out["len_range"]
    df_out["first"] = [df.iloc[ifirst[icol],icol] if ifirst[icol] >= 0 else bad_value
        for icol in range(ncol)]
    df_out["last"] = [df.iloc[ilast[icol],icol] if ilast[icol] >= 0 else bad_value
        for icol in range(ncol)]
    df_res = pd.merge(df_out,col_funcs_df(df, funcs).T,left_index=True,right_index=True)
    return df_res.rename(columns=func_renames)

def print_return_stats(df_ret, transpose=False, title=None, trailer=None,
    label="return stats:\n", ret_scale:float=1.0, print_nobs_col=True,
    print_correl=False, end=None, renames=func_renames, min_obs=1,
    round_rows=1, date_min=None, date_max=None, few_stats=False,
    sort_crit=None) -> None:
    """ Print return stats on each column of df_ret. round_rows = 1 is
    intended so that the row corresponding to #obs is printed as integers """
    if df_ret is None:
        return
    if date_min is not None or date_max is not None:
        df_ret = df_ret.copy()
        df_ret = subset_index(df_ret, date_min, date_max)
    if isinstance(df_ret, pd.Series):
        print_return_stats(pd.DataFrame(df_ret), title=title,
            trailer=trailer, label=label, ret_scale=ret_scale, end=end)
        return
    if title == "":
        print()
    elif title:
        print(title, end="")
    if df_ret.shape[0] * df_ret.shape[1] == 0:
        return
    print("#sym, #obs = ",df_ret.shape[1], " ", df_ret.shape[0], "\n",
        df_ret.index[0], " to ", df_ret.index[-1], sep="")
    if df_ret.isna().all().all():
        print("no valid data")
        return
    if ret_scale != 1.0:
        print("ret_scale =", ret_scale)
    profit_funcs_use = few_profit_funcs if few_stats else profit_funcs
    df_stats = col_funcs_df(ret_scale*df_ret, profit_funcs_use).rename(index=renames)
    if sort_crit is not None:
        df_stats = df_stats.loc[:, df_stats.loc[sort_crit].sort_values(ascending=False).index]
    if print_nobs_col:
        try:
            df_stats.loc["#obs"] = np.array(df_ret.apply(lambda x: np.sum(np.isfinite(x))))
            df_stats.loc["#obs"] = df_stats.loc["#obs"].astype(int)
        except Exception:
            df_stats.loc["#obs"] = -1 # signal an error
        df_stats = pd.concat([df_stats.loc[["#obs"]], df_stats.drop("#obs")])
    if transpose:
        df_stats = df_stats.T
        if print_nobs_col:
            col = df_stats.pop("#obs")
            df_stats.insert(0, col.name, col)
            df_stats = df_stats[df_stats["#obs"] >= min_obs]
    df_stats = convert_int_columns(df_stats)
    str_df_stats = df_stats.to_string()
    if not transpose and print_nobs_col and round_rows is not None and \
        round_rows > 0:
        str_df_stats = round_rows_df_string(str_df_stats, nrow=round_rows)
    if label:
        print(label, str_df_stats, sep="")
    else:
        print(str_df_stats, sep="")
    if print_correl and df_ret.shape[1] > 1:
        corr_matrix = df_ret.corr()
        corr_matrix.columns.name = corr_matrix.index.name = None
        print("\ncorrelations:\n", corr_matrix.to_string(), sep="")
    if trailer:
        print(trailer, end="")
    if end:
        print(end=end)

def read_csv_date_index(infile, date_col=0, date_min=None, date_max=None, nrows=None,
    ncol=None, print_fl:bool=False, print_fl_original:bool=False, check_numeric=False,
    print_stats_col=False, exclude_dates_month_day=None, columns=None,
    regex_col=None, verbose=False, allow_object_col=True,
    exclude_columns=None) -> pd.DataFrame:
    """
    Reads a CSV file into a DataFrame, sets a specified column as a date index, and optionally filters rows and columns.
    :param infile: Path to the CSV file.
    :param date_col: Index of the column to be used as the date index. Default is 0.
    :param date_min: Minimum date to filter the DataFrame. Default is None.
    :param date_max: Maximum date to filter the DataFrame. Default is None.
    :param nrows: Number of rows to read from the file. Default is None.
    :param ncol: Number of columns to read from the file. Default is None.
    :param print_fl: Flag to print first and last rows of the DataFrame. Default is False.
    :param print_fl_original: Flag to print first and last rows of the original DataFrame before processing. Default is False.
    :param check_numeric: Checks if all columns are numeric and prints those that are not. Default is False.
    :param print_stats_col: Flag to print descriptive statistics of the DataFrame. Default is False.
    :regex_col: Optional regular expression to use in filtering column names
    :return: Returns the processed DataFrame.
    """
    full_file_name = os.path.join(param.DATA_DIR, infile)
    df = pd.read_csv(full_file_name, nrows=nrows)
    if verbose is None or verbose:
        print("in read_csv_date_index, read", full_file_name) # debug
    data_files_read.append(full_file_name)
    if print_fl_original:
        print_first_last(df, title="\nread from " + full_file_name + ":", print_index=False,
            end="\n")
    df.iloc[:,date_col] = pd.to_datetime(df.iloc[:,date_col]).dt.date
    df = df.set_index(df.columns.values[date_col])
    if df.index.isnull().any():
        raise ValueError("Error: The file " + infile +
            " contains missing index values (NaNs).")
    if not allow_object_col and any(df.dtypes == 'object'):
        print("df.dtype =", df.dtypes)
        raise ValueError("Error: The dataframe read from file " + infile +
            "\nhas columns of type object, likely indicating bad data.")
    if not df.index.is_monotonic_increasing:
        print("in read_csv_date_index, reading", infile +
            ", df.index not ascending")
        print("non_ascending_rows(df):\n", non_ascending_rows(df),
            sep="")
        sys.exit()
    if date_min or date_max:
        df = df[date_min:date_max]
    if exclude_dates_month_day:
        df = exclude_dates_by_month_day(df, exclude_dates_month_day)
    if ncol and ncol < df.shape[1]:
        df = df.iloc[:,:ncol]
    if columns is not None:
        df = df[[col for col in columns]]
    if exclude_columns is not None:
        df = df[[col for col in df.columns if col not in exclude_columns]]
    df.index.rename("Date", inplace=True)
    if print_fl:
        print_first_last(df)
    if check_numeric:
        numeric_df = all_columns_numeric(df)
        if not numeric_df:
            print_non_numeric_columns(df)
            print("non-numeric columns in read_csv_date_index()")
            sys.exit()
    if print_stats_col:
        print_stats(df)
    if regex_col is not None:
        df = matching_columns(df, regex_col)
    return df

def print_first_last(df:pd.DataFrame, title=None, print_index=True, trailer=None,
    transpose=False, end=None, stats=False, ratio=False) -> None:
    """ Print shape and first and last rows of dataframe. If
    ratio is True also print the ratio of the last row to the
    first. """
    if title is not None:
        if title == "":
            print(end="\n")
        else:
            print(title)
    if isinstance(df, pd.Series):
        print_first_last_series(df, title=title, print_index=print_index, trailer=trailer,
            end=end)
        return
    print("#sym, #obs =", df.shape[1], df.shape[0])
    if len(df) > 0:
        df_fl = df.iloc[[0, -1], :]
        if ratio:
            df_fl.loc["ratio"] = df.iloc[-1] / df.iloc[0]
        if transpose:
            df_fl = df_fl.T
        print(df_fl.to_string(index=print_index))
    if stats:
        print_stats(df, title="\n", print_shape=False)
    if trailer:
        print(trailer, end="")
    if end:
        print(end=end)

def col_funcs_df(df:pd.DataFrame, funcs) -> pd.DataFrame:
    """ return a dataframe where each row contains the values of a function
    in funcs applied to the columns of df """
    return pd.DataFrame(col_funcs(df, funcs), columns=df.columns,
        index=[func.__name__ for func in funcs])

def col_funcs(df:pd.DataFrame, funcs) -> npt.NDArray:
    """ return a matrix where each row contains the values of a function
    in funcs applied to the columns of df """
    ncol = df.shape[1]
    nfunc = len(funcs)
    mat = np.full(shape=(nfunc,ncol), fill_value = 0.0)
    for ifunc in range(nfunc):
        mat[ifunc, :] = col_func(df, funcs[ifunc])
    return mat

def col_func(df:pd.DataFrame, func, dropna=True) -> npt.NDArray:
    """ return an array containing func applied to each column of df """
    if dropna:
        return np.array([safe_apply(func, df.iloc[:, icol].dropna())
            for icol in range(df.shape[1])])
    else:
        return np.array([safe_apply(func, df.iloc[:, icol])
            for icol in range(df.shape[1])])

def safe_apply(func, col_data):
    """
    Apply a function to a Series safely.
    Return np.nan if the Series is empty or if an error occurs during function application.
    """
    if col_data.empty:
        return np.nan
    try:
        result = func(col_data)
    except (FloatingPointError, RuntimeWarning, ValueError):
        result = np.nan
    return result

def convert_int_columns(df):
    """Convert float columns to integer if all values are exactly integers."""
    for column in df.columns:
        try:
            if all(df[column].apply(lambda x: x.is_integer())):
                df[column] = df[column].astype(int)
        except Exception:
            pass
    return df

def first_last_true_pos_by_column(df:pd.DataFrame) -> Tuple[npt.NDArray, npt.NDArray]:
    """ return numpy arrays containing the first and last true positions
    in each column of df """
    ncol = df.shape[1]
    ifirst = np.full(shape=ncol, fill_value=-1)
    ilast  = np.full(shape=ncol, fill_value=-1)
    y = df.to_numpy()
    for icol in range(ncol):
        ifirst[icol], ilast[icol] = first_last_true_pos(y[:,icol])
    return ifirst, ilast
