import unittest

import numpy as np
import pandas as pd

from .base import AbstractNvd3Chart, Axis, Series
from .utils import teardown, teardown_series, teardown_frame, teardown_index
from ._compat import integer_types


class TestAbstractNvd3Chart(unittest.TestCase):

    def setUp(self):
        class Nvd3Chart(AbstractNvd3Chart):
            _model = 'Nvd3Chart'

            def add_axis(self, *args, **kwargs):
                super(Nvd3Chart, self).add_axis(*args, **kwargs)

            def add_series(self, *args, **kwargs):
                super(Nvd3Chart, self).add_series(*args, **kwargs)

        self.chart = Nvd3Chart

    def test_bare_javascript(self):
        """
        Test expected javascript for chart initialized with no data, series,
        or axis.
        """
        chart = self.chart()

        result = chart.javascript
        expected = """
<script>
    nv.addGraph(function() {
        var data=[];
        var chart = nv.models.Nvd3Chart();

        d3.select('#chart svg')
          .datum(data)
          .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
</script>
        """

    def test_model_must_be_defined(self):
        """Is an error raised when `_model` isn't defined?"""

        class Chart(AbstractNvd3Chart):

            def add_axis(*args, **kwargs):
                super(Chart, self).add_axis(*args, **kwargs)

            def add_series(*args, **kwargs):
                super(Chart, self).add_series(*args, **kwargs)

        self.assertRaises(NotImplementedError, Chart)

    def test_axis_writer(self):
        chart = self.chart()
        chart.add_axis('xAxis')

        script = []
        chart._write_axis(script)

        # ignore tabs and newlines
        script = [line.strip() for line in script]

        # first line should give name of axis
        self.assertEqual('chart.xAxis', script[0])

        # check every attribute is written into script
        for attribute, value in chart.axes['xAxis'].to_dict().items():
            self.assertTrue('%s.%s' % (attribute, value) in script)

    def test_add_axis_creates_axis(self):
        chart = self.chart()
        chart.add_axis('xAxis')

        self.assertTrue('xAxis' in chart.axes)

        for axis in chart.axes.values():
            self.assertTrue(isinstance(axis, Axis))

    def test_add_series_creates_series(self):
        chart = self.chart()
        chart.add_series()

        for series in chart.series.values():
            self.assertTrue(isinstance(series, Series))

    def test_add_series_gives_default_name(self):
        """
        Do new series get named properly?
        """
        chart = self.chart()

        chart.add_series()
        chart.add_series('New Series')
        chart.add_series()

        for series in ('Series1', 'New Series', 'Series3'):
            self.assertTrue(series in chart.series)


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


class TestSeries(unittest.TestCase):

    def test_empty_series(self):
        series = Series('Series1')

        self.assertEqual(series.x, [])
        self.assertEqual(series.y, [])

    def test_series_to_dict(self):
        x, y = [0,1], [1,2]
        series = Series('Series1', x, y)
        result = series.to_dict()

        self.assertEqual(result['key'], 'Series1')
        self.assertEqual(result['values'], [{'x': 0, 'y': 1}, {'x': 1, 'y':2}])


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
            self.assertTrue(isinstance(i, integer_types))

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

        data = list(range(2))
        series = pd.Series(data)
        result = teardown_series(series)
        expected = {
            'name': None,
            'x': data,
            'y': data
        }

        self.assertEqual(result, expected)

    def test_series_empty(self):
        """
        Broken down series should be empty list
        """

        data = pd.Series()
        result = teardown_series(data)
        self.assertEqual(result['x'], [])
        self.assertEqual(result['y'], result['x'])

    def test_series_with_nan_and_infinite(self):
        """
        Are NaN values not included in result?
        """

        data = pd.Series([1, np.nan, np.inf])
        result = teardown_series(data)
        expected = {
            'name': None,
            'x': [0,],
            'y': [1,]
        }

        self.assertEqual(result, expected)

    def test_dataframe_teardown(self):
        data = pd.DataFrame([(1,2), (0,3)], columns=['a','b'])
        result = teardown_frame(data)
        expected = [
            {'name': 'a', 'x': [0,1], 'y': [1,0]},
            {'name': 'b', 'x':[0,1], 'y':[2,3]}
        ]

        self.assertEqual(result, expected)
