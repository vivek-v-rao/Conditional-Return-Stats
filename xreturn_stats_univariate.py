""" read time series data from CSV and print stats on returns """
import pandas as pd
import numpy as np
from pandas_util import (read_csv_date_index, print_first_last,
    print_return_stats, first_last_good_dates, tail_counts,
    min_max_indices_values)
import param
from util import print_all_vars
from date_util import date_ymd

pd.set_option("display.float_format", "{:.3f}".format)
print_date_ranges = False
param.obs_year = 252.0
ret_scale = 100.0
rf_rate = 0.0
thresh = np.array([2.5, 5.0, 10.0])
ret_type = "simple"
infile = "gspc_vix.csv"
indic = "VIX"
indic_thresh = 25
event_abs_ret_thresh = 2.5
max_col = None
print_first_last_prices = False
date_min = date_ymd(1990, 1,  2) # None
date_max = date_ymd(2026, 3, 31)
dropna_dates = False
dropna_sym = False
transpose_stats = True
call_print_return_stats = True
call_min_max = True
allowed_symbols = None # ["SPY", "EFA", "TLT", "SHY"]
freq_scale = 100.0
print_big = False
print_all_vars(globals())

df = read_csv_date_index(infile, date_min=date_min, date_max=date_max).iloc[:,:max_col]
if allowed_symbols is not None:
    df = df[[c for c in allowed_symbols if c in df.columns]]
if dropna_dates:
    df.dropna(axis=0, how="any", inplace=True)
if dropna_sym:
    df.dropna(axis=1, how="any", inplace=True)
if print_first_last_prices:
    print_first_last(df, title="\n")

if ret_type == "simple": # simple returns
    df_ret = ret_scale * (df.pct_change(fill_method=None)[1:] - rf_rate/param.obs_year)
elif ret_type == "log":  # log returns
    df_ret = ret_scale * (df.apply(np.log).diff() - rf_rate/param.obs_year)

indic_prior = df[indic].shift(1).loc[df_ret.index]
df_ret_indic_hi = df_ret.loc[indic_prior >= indic_thresh]
df_ret_indic_lo = df_ret.loc[indic_prior < indic_thresh]

first_asset = df_ret.columns[0]
mask_big_move = df_ret[first_asset].abs() >= event_abs_ret_thresh
df_big_move = df_ret.loc[mask_big_move].copy()
df_big_move.insert(0, f"{indic}_prior", indic_prior.loc[df_big_move.index])

print("\n#returns, date range:", len(df_ret), df_ret.index[0], df_ret.index[-1])
print(f"#returns with prior {indic} >= {indic_thresh}:", len(df_ret_indic_hi))
print(f"#returns with prior {indic} < {indic_thresh} :", len(df_ret_indic_lo))

if print_date_ranges:
    print("\ndate ranges:\n", first_last_good_dates(df_ret).to_string(), sep="")

print("\nall returns:\n", end="")
if call_print_return_stats:
    print_return_stats(df_ret, transpose=transpose_stats)
    print(f"\nreturns conditional on prior {indic} >= {indic_thresh}:\n", end="")
    print_return_stats(df_ret_indic_hi, transpose=transpose_stats)
    print(f"\nreturns conditional on prior {indic} < {indic_thresh}:\n", end="")
    print_return_stats(df_ret_indic_lo, transpose=transpose_stats)

if call_min_max:
    print("\nreturn stats, all:\n", min_max_indices_values(df_ret).to_string())
    print(f"\nreturn stats, prior {indic} >= {indic_thresh}:\n", min_max_indices_values(df_ret_indic_hi).to_string())
    print(f"\nreturn stats, prior {indic} < {indic_thresh}:\n", min_max_indices_values(df_ret_indic_lo).to_string())

if thresh is not None:
    print("\nreturn counts, all:\n" + tail_counts(df_ret, thresh, freq_scale=freq_scale).to_string())
    print(f"\nreturn counts, prior {indic} >= {indic_thresh}:\n" +
        tail_counts(df_ret_indic_hi, thresh, freq_scale=freq_scale).to_string())
    print(f"\nreturn counts, prior {indic} < {indic_thresh}:\n" +
        tail_counts(df_ret_indic_lo, thresh, freq_scale=freq_scale).to_string())

if print_big:
    print(f"\nprior {indic} and all returns on {len(df_big_move)} dates where abs({first_asset} return) >= {event_abs_ret_thresh}:\n")
    print(df_big_move.to_string())
