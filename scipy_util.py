from scipy import stats

def mode_and_mode_count(x):
    """ Returns the mode and the count of the mode of array x. """
    mode_result = stats.mode(x, keepdims=True)
    return [mode_result.mode[0], mode_result.count[0]]
