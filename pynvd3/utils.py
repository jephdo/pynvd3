"""
    pynvd3.utils
    ~~~~~~~~~~~

    Functions for working with pandas DataFrames.
"""

from . import PANDAS_INSTALLED

if PANDAS_INSTALLED:
    from pandas import Series, DataFrame
    from pandas.core.index import MultiIndex
    from pandas.tseries.index import DatetimeIndex
    from numpy import isfinite


def teardown(data):
    """
    Return a dictionary from a DataFrame or Series. Dictionary is in the JSON
    form needed for NVD3.

    This function dispatches to :func:`teardown_series` 
    and :func:`teardown_frame`
    """

    if isinstance(data, Series):
        return teardown_series(data)
    if isinstance(data, DataFrame):
        return teardown_frame(data)

    raise TypeError('Data not recognized as DataFrame or Series: %s' % type(data))

def teardown_series(series):
    """
    Return a dictionary from a pandas Series.
    """

    # remove any nan or inf values since these values cannot be 
    # displayed on a chart
    series = series[series.notnull() & isfinite(series)]

    x_values = teardown_index(series.index)
    y_values = series.tolist()
    values = [{'x': x, 'y': y} for x,y in zip(x_values, y_values)]

    return {
        'name': series.name,
        'x': x_values,
        'y': y_values
    }

def teardown_frame(dataframe):
    """
    Return a dictionary from a pandas DataFrame.
    """

    return [teardown_series(dataframe[col])for col in dataframe.columns]


def teardown_index(index):
    """
    Converts an Index into a list of values. For DatetimeIndex's, timestamps 
    are converted into milliseconds after epoch.
    """

    if isinstance(index, MultiIndex):
        raise TypeError('Index cannot be of type `MultiIndex`: %s' % index)

    values = index.values.tolist()

    # pandas timestamps are stored as nanoseconds(ns) after epoch, 
    # convert from ns to milliseconds
    if isinstance(index, DatetimeIndex):
        values = [v // 1000000 for v in values]

    return values
