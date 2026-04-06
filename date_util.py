""" date utilities """
import re
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
from numpy import ndarray
from numpy_util import first_pos_values, last_pos_values, reference_period
from util import index
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from collections import namedtuple
import calendar
EARLIEST_YEAR = 1940
DAYS_IN_YEAR = 365
MONTHS_IN_YEAR = 12
BAD_MONTH = -1
FUTURES_MONTH_CODES = ["F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]
DateLag = namedtuple("DateLag", "eom months_later days_later")
DateLag.__new__.__defaults__ = (False, 0, 0)

def month_num_from_month_code(letter: str) -> int:
    """ return the month integer (Jan = 1 etc.) given a futures month code letter,
    BAD_MONTH if no match """
    try:
        month_num = FUTURES_MONTH_CODES.index(letter) + 1
    except:
        month_num = BAD_MONTH
    return month_num

def exp_date_futures_symbol(futures_symbol: str) -> date:
    """ return a date corresponding to a futures month letter followed by a 2-digit year, so
        for example "H23" becomes 2023-03-01 """
    DAY_OF_MONTH = 1
    year = int(futures_symbol[-2:])
    month_code = futures_symbol[-3]
    return datetime(year_4_digit_from_2(year), month_num_from_month_code(month_code), DAY_OF_MONTH).date()

def year_4_digit_from_2(iyear:int, earliest_year:int = EARLIEST_YEAR) -> int:
    """ convert a 2-digit year such as 23 to a 4-digit year such as 2023 """
    if iyear > 99:
        # assume the input is already a 4-digit year
        return iyear
    jyear = iyear + 1900
    if jyear < earliest_year:
        jyear += 100
    return jyear


def prior_month(xdate: date, day_of_month=None) -> date:
    """ return a date one month earlier than xdate """
    # increases the month by one and leaves the day-of-month
    # unchanged, unless day_of_month specified. This could
    # produce an invalid date such as Feb 30
    year, month, day = (xdate.year, xdate.month-1, xdate.day)
    if month < 1:
        month = month + MONTHS_IN_YEAR
        year = year - 1
    if day_of_month:
        day = day_of_month
    return datetime(year, month, day).date()

def yyyym(futures_sym: str) -> str:
    """ return the year and month in the form YYYYM given a futures symbol, where
        M is a futures month code (Jan = F, etc.), and converting 2-digit
        years to 4-digit years. Assume the futures_sym has a month-code and
        year in the last 3 characters, for example 'ESH23', for which
        '2023H' is returned """
    yym = futures_sym[-2:] + futures_sym[2] # get for example "23H" from "ESH23"
    y2d = int(yym[:2])                      # get for example 23 from "23H"
    return str(year_4_digit_from_2(y2d)) + yym[2]




def year_from_sym(futures_sym: str) -> int:
    """ return a 4-digit year from a futures symbol such as 'BOF60' or 'XBZ26' """
    yyyym_str = yyyym(futures_sym)
    return int(yyyym_str[:4])

def roll_date_futures_symbol(futures_symbol: str, day_of_month: int=10) -> date:
    return prior_month(exp_date_futures_symbol(futures_symbol),
        day_of_month=day_of_month)

def roll_dates_futures_symbols(futures_symbols: list[str], day_of_month: int=10) -> ndarray:
    return np.array([roll_date_futures_symbol(x, day_of_month)
        for x in futures_symbols])


def date_to_float(date):
    """ convert date to float in units of years, for example 2010-10-01 to 2010.75 """
    return date.year + frac_year(date.month, date.day)

def frac_year(month, day):
    """ return the fraction of the year elapsed """
    return (month-1)/MONTHS_IN_YEAR + (day-1)/DAYS_IN_YEAR



def consec_dates(n, date_min_str="2000-01-01"):
    """ return n consecutive dates starting with date_min_str """
    return list(rrule(DAILY, count=n, dtstart=parse(date_min_str)))

def pos_last_date_months(dates):
    """ return the positions of the last dates in the month """
    return last_pos_values(dates.month)

def pos_first_date_months(dates):
    """ return the positions of the first dates in the month """
    return first_pos_values(dates.month)






def eomonth(xdate, nmonths_later=0, ndays_later=0):
    """
    Calculate the last day of the month for a date that is 'nmonths_later' months
    from the 'xdate'. Similar to eomonth of Microsoft Excel, but with an
    added ndays_later argument.
    Parameters:
    xdate (datetime.date): The starting date.
    nmonths_later (int): Number of months to add to the original date.
    ndays_later (int): Number of days to add to the computed end-of-month date
    Returns:
    datetime.date: The date representing the last day of the month, 'nmonths_later'
    months from the original date.
    """
    # Add 'nmonths_later' months to the date and move to the first day of the next month
    future_month_first_day = xdate + relativedelta(months=nmonths_later+1, day=1)
        # Subtract one day to get the last day of the desired month
    last_day_of_future_month = future_month_first_day - relativedelta(days=1-ndays_later)
    return last_day_of_future_month

def month_ends(first_month_end, num_months):
    """
    Generate a 1D numpy array of datetime.date objects for consecutive month-ends.
    Parameters:
    - first_month_end (str): The first month-end date in 'YYYY-MM-DD' format.
    - num_months (int): The number of month-ends to generate.
    Returns:
    - numpy.ndarray: An array of datetime.date objects.
    """
    # Convert the first_month_end string to a datetime object
    start_date = pd.to_datetime(first_month_end)
    # Generate the date range with month end frequency
    date_range = pd.date_range(start=start_date, periods=num_months, freq='M')
    # Convert to numpy array of datetime.date
    month_ends = np.array([date.date() for date in date_range])
    return month_ends

def date_ymd(year, month, day):
    """ create datetime.date from year, month, day """
    return datetime(year, month, day).date()











