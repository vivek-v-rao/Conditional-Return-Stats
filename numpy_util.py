""" Utility functions for NumPy """
from typing import Tuple
import numpy as np
import numpy.typing as npt
import warnings
warnings.filterwarnings('ignore', message='Mean of empty slice', category=RuntimeWarning)

def first_true_pos(x: npt.NDArray) -> int:
    """ for logical ndarray x, returns the index of the first True value
    if any, otherwise -1 """
    if len(x) < 1:
        return -1
    i = np.argmax(x)
    if x[i]:
        return int(i)
    return -1

def first_last_true_pos(x: npt.NDArray) -> Tuple[int,int]:
    """ return locations of first and last true positions in ndarray x """
    ipos = np.flatnonzero(x)
    if len(ipos) > 0:
        return (ipos[0],ipos[-1])
    else:
        return (-1,-1)

def last_true_pos(x: npt.NDArray) -> int:
    """ return location of last true position in ndarray x, -1 if none true """
    ipos = np.flatnonzero(x)
    return ipos[-1] if len(ipos) > 0 else -1



def new_rows_matrix(x: npt.NDArray) -> npt.NDArray:
    """ return an ndarray of the first row and following rows that differ
    from the previous row """
    nr = x.shape[0]
    irow = []
    if nr > 0:
        irow.append(0)
    for i in range(1,nr):
        if not np.array_equal(x[i,:],x[i-1,:]):
            irow.append(i)
    return np.array(irow)







def seasonal_ma(x:npt.NDArray, ma_length:int, period:int = 1) -> npt.NDArray:
    """ Compute the seasonal rolling moving average. For monthly data, period=12
    would give the moving average for the same month over the last ma_length years """
    debug = False
    if debug:
        print("\nentered seasonal_ma, ma_length, period, type(x), x.shape =",
            ma_length, period, type(x), x.shape) # debug
    n = len(x)
    y = np.full(n, np.nan)
    if ma_length < 1 or period < 1:
        return y
    back = (ma_length-1)*period
    for i in range(ma_length-1, n):
        ifirst = i-back
        if debug:
            print(i, ifirst, i+1, x[ifirst:i+1:period]) # debug
        vec = x[ifirst:i+1:period]
        if len(vec) > 0 and ifirst >= 0:
            y[i] = np.mean(x[ifirst:i+1:period])
    if debug:
        print("exited seasonal_ma")
    return y


def detrended_geo(x:npt.NDArray) -> npt.NDArray:
    """ geometrically detrend x """
    good = np.isfinite(x)
    y = x.copy()
    y[good] = detrended_geo_no_nan(x[good])
    return y

def detrended_geo_no_nan(x:npt.NDArray) -> npt.NDArray:
    """ geometrically detrend x assuming no NaN """
    n = len(x)
    if n < 1:
        return x
    ratio = x[-1]/x[0]
    return x*np.geomspace(ratio, 1.0, n)

def shifted_positive(x: npt.NDArray, num_sd:float=1.0) -> npt.NDArray:
    """ shift data so that it is always positive if the original data has
    nonzero standard deviation """
    xmin = np.min(x)
    if xmin > 0:
        return x
    xsd = np.std(x)
    return x - xmin + num_sd*xsd


def count_non_nan(x: npt.NDArray) -> int:
    """ count number of non-NaN elements in array """
    return np.count_nonzero(~np.isnan(x))

def count_nonzero_non_nan(x: npt.NDArray) -> int:
    """ count number of non-NaN values that are nonzero """
    return np.count_nonzero(~np.isnan(x) & (x != 0))

def true_ranges(bool_array):
    """
    Identifies ranges of consecutive True values in a 1D numpy array of booleans.
    Parameters:
    - bool_array (np.ndarray): A 1D numpy array of booleans.
    Returns:
    - np.ndarray: A 2D numpy array with two columns, where each row contains the start and end indices
      of consecutive True ranges in the input array.
    """
    # Initialize an empty list to store start and end indices of consecutive True ranges
    ranges = []
    # Initialize the start index of the current range of Trues to None
    start_index = None
    # Iterate over the array to find ranges of True values
    for i, value in enumerate(bool_array):
        if value:
            if start_index is None:
                start_index = i  # Mark the start of a new range of Trues
        else:
            if start_index is not None:
                # End of current range of Trues found; add the range to the list
                ranges.append([start_index, i])
                start_index = None  # Reset start_index for the next range of Trues
    # Check if the last element is True and hence a range ends with the last element
    if start_index is not None:
        ranges.append([start_index, len(bool_array)])
    # Convert the list of ranges to a 2D numpy array and return
    return np.array(ranges)

def func_blocks(x: np.ndarray, k: int, func, include_last=True):
    """
    Applies a specified function to blocks of length k in a 1-D array and returns the results.
    This function divides the input array `x` into blocks of size `k` and applies a given function `func`
    to each block. Blocks are formed column-wise in a temporary 2-D array before function application.
    Parameters:
    - x (np.ndarray): Input 1-dimensional numpy array.
    - k (int): Block size, indicating how many elements each block contains.
    - func (callable): A function to be applied to each block. Should accept a 1-D numpy array and return a single value.
    - include_last (bool): If True, includes the last block even if it's smaller than `k` (by padding with `np.nan`).
                           Defaults to True.
    Returns:
    - np.ndarray: A 1-D numpy array of the results obtained by applying `func` to each block.
                  Returns None if `k` is less than 1 or greater than the length of `x`.
    """
    if k < 1 or k > len(x):
        return None
    xmat = column_blocks(x, k, include_last)
    return np.apply_along_axis(func, 0, xmat)

def first_pos_values(arr):
    """ Return the locations of new elements in a 1-D NumPy array. """
    ipos = np.where(np.diff(arr) != 0)[0] + 1
    if len(arr) > 0:
        ipos = np.insert(ipos, 0, 0)
    return ipos

def last_pos_values(arr):
    """ Return the locations of elements preceding changes in a 1-D NumPy array. """
    diff = np.diff(arr)
    ipos = np.where(diff != 0)[0]
    n = len(arr)
    if n > 0:
        ipos = np.append(ipos, n-1)
    return ipos

def reference_period(ivec, value_new_period):
    """ return a 1-d array of integers starting with 1 that increases by 1 when
    ivec changes from value_new_period - 1 to value_new_period """
    changed = (ivec == value_new_period) & (np.roll(ivec, shift=1) == value_new_period - 1)
    return 1 + np.cumsum(changed)




