""" statistics utilities """
import numpy as np
import numpy.typing as npt
from scipy import stats
import param

def acf(x: npt.NDArray, nlags: int = 5):
    """ return autocorrelations of time series x """
    return sm.tsa.acf(x, nlags=nlags)[1:]

def annmean(xret: npt.NDArray, obs_year=None) -> float:
    """ return the annualized mean """
    return np.mean(xret) * (obs_year if obs_year else param.obs_year)

def vol(xret: npt.NDArray, obs_year=None) -> float:
    """ return the annualized volatility """
    return np.std(xret) * np.sqrt(obs_year if obs_year else param.obs_year)

def meanabs(x: npt.NDArray) -> float:
    """ return the mean absolute value """
    return np.mean(np.abs(x))

def Sharpe(xret: npt.NDArray, obs_year=None) -> float:
    """ return the Sharpe ratio """
    if len(xret) < 1:
        return np.nan
    obs_year_ = obs_year if obs_year else param.obs_year
    stdev = np.std(xret)
    if stdev > 0:
        return np.sqrt(obs_year_) * np.mean(xret)/stdev
    else:
        return np.nan


def Sharpe_adj(xret: npt.NDArray, obs_year=None) -> float:
    """ return the Sharpe ratio adjusted for skew and kurtosis. Reference:
    Pezier, Jaques and White, Anthony. 2006. The Relative Merits of Investable Hedge
    Fund Indices and of Funds of Hedge Funds in Optimal Passive Portfolios."""
    xsharpe = Sharpe(xret, obs_year)
    if len(xret) < 3:
        return xsharpe
    try:
        xskew = stats.skew(xret)
        xkurt = stats.kurtosis(xret)
        return Sharpe_adj_from_moments(xsharpe, xskew, xkurt)
    except (FloatingPointError, RuntimeWarning, ValueError) as e:
        print(f"Warning: {e}. Returning xsharpe.")
        return xsharpe

def Sharpe_adj_from_moments(xsharpe, xskew, xkurt):
    """ return the Sharpe ratio adjusted for known skew and kurtosis."""
    return xsharpe * (1 + (xskew/6) * xsharpe - (xkurt/24) * xsharpe**2)

def correl(x, y, filter_nan=False):
    """ return the correlation coefficient between 2 1-D arrays """
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore") # suppress division by zero errors if x or y
        # have zero standard deviation or no good data
        if filter_nan:
            good = np.isfinite(x) & np.isfinite(y)
            if np.sum(good) > 1:
                return np.corrcoef(x[good], y[good])[0,1]
            else:
                return 0.0
        else:
            return np.corrcoef(x,y)[0,1]

def max_drawdown(x: npt.NDArray) -> float:
    """ return the maximum drawdown of a series of levels """
    n = len(x)
    if n < 2:
        return 0.0
    max_dd = 0.0
    running_max = x[0]
    for i in range(1, n):
        if x[i] < running_max:
            max_dd = max(max_dd, running_max - x[i])
        else:
            running_max = x[i]
    return max_dd

def max_drawdown_returns(x: npt.NDArray) -> float:
    """ return the maximum drawdown of a series of returns """
    return max_drawdown(np.insert(x.cumsum(), 0, 0.0))

def maxDD(x: npt.NDArray) -> float:
    """ return the maximum drawdown of a series of returns """
    return max_drawdown_returns(x)

def cumul_div_maxDD(x: npt.NDArray) -> float:
    """ return the sum of returns divied by the maximum drawdown """
    xdraw = max_drawdown_returns(x)
    if np.isinf(xdraw):
        return np.nan
    xsum = np.sum(x)
    return np.nan if (np.isinf(xsum) or xdraw <= 0) else xsum/xdraw
