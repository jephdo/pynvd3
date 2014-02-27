import unittest

import numpy as np
import pandas as pd

from .base import Axis
from .utils import teardown, teardown_series, teardown_frame, teardown_index


# class TestAbstractNvd3Chart(unittest.TestCase):
#     def setUp(self):
#         class Nvd3Chart(TestAbstractNvd3Chart):
#             def add_series(*args, **kwargs):
#                 super().add_series(*args, **kwargs)


#         self.chart = Nvd3Chart

#     def test_write_method(self):
#         chart = self.chart()
#         self.chart.write('hello')
#         self.chart.write('world', indent=2)

#         expected = ['hello', '\t\tworld']
#         self.assertEqual(expected, self.chart.javascript)

#     def test_add_series(self):
#         chart = self.chart()
#         data = {'x': [1,2], 'y': [4.2, 5]}
        
#         chart.add_series(data, name='Stock Price')
#         self.assertEqual(chart.series['Stock Price'], data)

#         chart.add_series(data)
#         self.assertEqual(chart.series['Series2'], data)


class TestAxis(unittest.TestCase):

    def test_valid_axes_names(self):
        """
        Are axes named 'xAxis', 'y1Axis', 'y2Axis'?
        """

        for name in ('xaxis', 'xaxis1', 'not_an_axis', 'y3Axis'):
            self.assertRaises(AssertionError, Axis, name='xaxis')

    def test_axis_show_max_min(self):
        axis = Axis('xAxis', show_max_min=False)
        result = axis.to_dict()['showMaxMin']
        self.assertEqual(result, 'false')

        axis = Axis('xAxis', show_max_min=True)
        self.assertTrue('showMaxMin' not in result)

    def test_axis_labels(self):
        axis = Axis('xAxis', stagger_labels=True, rotate_labels=-15)
        result = axis.to_dict()

        self.assertEqual(result['staggerLabels'], 'true')
        self.assertEqual(result['rotateLabels'], -15)

    def test_tick_format_is_date(self):
        """
        Is tick format properly recognized as a time format?
        """
        axis = Axis('xAxis')

        for char in 'aAbBcdeHIjmMLpSUwWxXyYZ':
            self.assertTrue(axis._check_tick_format_is_date('%%%s' % char))

        for format in (',.0f', '04d', '.0%', '%z'):
            self.assertFalse(axis._check_tick_format_is_date(format))


class TestUtilsTearDowns(unittest.TestCase):

    def test_index_converts_x_values(self):
        """
        Does the index get converted into a list of values?
        """

        int_index = pd.Index(list(range(10)))
        result = teardown_index(int_index)
        expected = list(range(10))

        self.assertTrue(isinstance(result, list))
        self.assertEqual(result, expected)

    def test_datetime_index_converts_x_values(self):
        """
        Does a DatetimeIndex get converted into a list of milliseconds
        after epoch?
        """

        datetime_index = pd.date_range('1-1-2000', '1-10-2000')
        result = teardown_index(datetime_index)

        expected = [
            946684800000, 946771200000, 946857600000, 946944000000,
            947030400000, 947116800000, 947203200000, 947289600000,
            947376000000, 947462400000
        ]

        self.assertEqual(result, expected)

        # all values should be integers not floats since it's supposed to be 
        # number of milliseconds after epoch
        for i in result:
            self.assertTrue(isinstance(i, int))

    def test_no_multiindexes(self):
        """
        Only teardown single indexes.
        """
        from pandas.core.index import MultiIndex

        index = MultiIndex.from_tuples([(0,1), (1,2)])
        self.assertRaises(TypeError, teardown_index, index)

    def test_series_to_dict(self):
        """
        Are Series broken down into dicts?
        """

        data = pd.Series(list(range(2)))
        result = teardown_series(data)
        expected = {
            'name': None,
            'values': [{'x': i, 'y': i }for i in range(2)]
        }

        self.assertEqual(result, expected)

    def test_series_empty(self):
        """
        Broken down series should be empty list
        """

        data = pd.Series()
        result = teardown_series(data)
        self.assertEqual(result['values'], [])

    def test_series_with_nan_and_infinite(self):
        """
        Are NaN values not included in result?
        """

        data = pd.Series([1, np.nan, np.inf])
        result = teardown_series(data)
        expected = {
            'name': None,
            'values': [{'x': 0, 'y': 1}]
        }

        self.assertEqual(result, expected)

    def test_dataframe_teardown(self):
        data = pd.DataFrame([(1,2), (0,3)], columns=['a','b'])
        result = teardown_frame(data)
        expected = [
            {'name': 'a', 'values': [{'x': 0, 'y': 1}, {'x': 1, 'y': 0}]},
            {'name': 'b', 'values': [{'x': 0, 'y': 2}, {'x': 1, 'y': 3}]},
        ]

        self.assertEqual(result, expected)
