"""
    nvd3.base
    ~~~~~~~~~~~

    Base classes and objects for constructing charts. Each chart type should 
    inherit from :class:`AbstractNvd3Chart` and implement the necessary
    constructor methods.
"""

import abc
import json
import re

from . import PANDAS_INSTALLED

if PANDAS_INSTALLED:
    from .utils import teardown


COLOR_HEX_CODES = {
    'blue': '#1f77b4',
    'orange': '#ff7f0e',
    'green': '#2ca02c',
    'red': '#d62728',
    'purple': '#9467bd',
    'brown': '#8C564b',
    'pink': '#e377c2',
    'gray': '#7f7f7f',
}

class AbstractNvd3Chart(object):

    __metaclass__ = abc.ABCMeta

    # name of the NVD3.js chart type e.g. 'lineChart', 'multiBarChart'
    # also see: https://github.com/novus/nvd3/tree/master/src/models
    _model = None

    def __init__(self, chart_id='chart'):
        if self._model is None:
            raise NotImplementedError('NVD3 model type not defined')

        self.chart_id = chart_id
        self.series = {}
        self.axes = {}

    @abc.abstractmethod
    def add_axis(self, *args, **kwargs):
        axis = Axis(*args, **kwargs)
        self.axes[axis.name] = axis

    @abc.abstractmethod
    def add_series(self, name=None, x=None, y=None):
        if name is None:
            name = "Series%s" % (len(self.series) + 1)

        series = Series(name, x, y)
        self.series[series.name] = series

    @property
    def javascript(self):
        script = []

        script.append("<script>")
        script.append("\tnv.addGraph(function() {")

        data = [series.to_dict() for series in self.series.values()]
        script.append("\t\tvar data=%s;" % json.dumps(data))
        script.append("\t\tvar chart = nv.models.%s();" % self._model)

        # allow hooks here

        for axis in self.axes.values():
            script.append('\t\tchart.%s' % axis.name)

            for attribute, value in axis.to_dict().items():
                script.append('\t\t\t.%s(%s)' % (attribute, value))

        script.append("\n\t\td3.select('#%s svg')" % self.chart_id)
        script.append("\t\t  .datum(data)")
        script.append("\t\t  .call(chart);")

        script.append("\n\t\tnv.utils.windowResize(chart.update);")

        script.append("\n\t\treturn chart;")

        script.append("\t});")
        script.append("</script>")

        return '\n'.join(script)

    @property
    def html(self):
        return '<div id=%s><svg /></div>' % self.chart_id

    @classmethod
    def from_dataframe(cls, dataframe, *args, **kwargs):
        if not PANDAS_INSTALLED:
            raise ImportError('Failed to create chart from DataFrame - cannot import pandas')

        cht = cls(*args, **kwargs)

        data = teardown(dataframe)

        return cht


class Axis(object):
    """
    Axis for an NVD3.js chart.

    :param name: The name of the axis e.g. 'xAxis' or 'yAxis'.
    :param label: Text to display as label of the axis e.g. "distance (km)".
    :param stagger_labels: Flag to stagger tick labels along the axis -- useful 
                           if text is too wide.
    :param rotate_labels: Degrees clockwise to rotate tick labels (can be 
                          a positive or negative integer).
    :param show_max_min: Flag to explicitly display a tick at both the 
                         smallest and largest values on the axis.
    :param tick_format: d3.js formatting specifier to format tick marks. 
                        See https://github.com/mbostock/d3/wiki/Formatting.
    """

    def __init__(self, name, label=None, stagger_labels=False, rotate_labels=0,
        show_max_min=True, tick_format=None):
        assert re.match('[xy][0-2]?Axis', name), \
            "Axis name must be one of 'xAxis', 'x1Axis', 'x2Axis', 'yAxis', 'y1Axis', 'y2Axis': %s" % name
        
        self.name = name
        self.label = label
        self.stagger_labels = stagger_labels
        self.rotate_labels = rotate_labels
        self.show_max_min = show_max_min
        self.tick_format = tick_format

    def to_dict(self):
        """
        Serializes the attributes of an instance of :class:`Axis` into a
        dictionary. Also converts values of attributes into javascript code.
        """

        axis = {}

        if not self.show_max_min:
            axis['showMaxMin'] = 'false'
        if self.label is not None:
            axis['axisLabel'] = self.label
        if self.stagger_labels:
            axis['staggerLabels'] = 'true'
        if self.rotate_labels:
            axis['rotateLabels'] = self.rotate_labels
        if self.tick_format:
            is_date = self._check_tick_format_is_date(self.tick_format)
            
            format = []
            if is_date:
                format.append("function(d) {")
                format.append("d3.time.format(%s)(new Date(d))}" % self.tick_format)
            else:
                format.append("d3.format(%s)" % self.tick_format)

            axis['tickFormat'] = ''.join(format)
        return axis

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def _check_tick_format_is_date(tick_format):
        """
        Returns `True` or `False` depending on if the specified axis tick 
        format is for a time series.
        """
        # when creating a time format specifier in d3, 
        # there are a defined set of directives e.g. %a, %H, %Z, etc.
        # See: https://github.com/mbostock/d3/wiki/Time-Formatting
        directives = 'aAbBcdeHIjmMLpSUwWxXyYZ'
        pattern = '%%[%s]' % directives
        
        return bool(re.match(pattern, tick_format))

    def __str__(self):
        return '<Axis: %s>\n%s' % (self.name, self.to_json())


class Series(object):

    def __init__(self, name, x=None, y=None):
        if x is None:
            x = []
        if y is None:
            y = []
        
        self.name = name
        self.x = x
        self.y = y

    def to_dict(self):
        series = {}

        series['key'] = self.name
        series['values'] = [{'x': x, 'y': y} for x,y in zip(self.x, self.y)]

        return series

    def to_json(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return '<Series: %s>\n%s' % (self.name, self.to_json())