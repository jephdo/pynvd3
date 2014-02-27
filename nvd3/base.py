"""
    nvd3.base
    ~~~~~~~~~~~

    Base classes and objects for constructing charts. Each chart type should 
    inherit from :class:`AbstractNvd3Chart` and implement the necessary
    constructor methods.
"""

import abc
import re

try:
    import ujson as json
except ImportError:
    import json


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

    def __init__(self, element_id):
        if self._model is None:
            raise NotImplementedError('NVD3 model type not defined')

        self.element_id = element_id

        self.series = {}
        self.axes = []
        self.javascript = []

    # def write(self, value, indent=0):
    #     self.javascript.append('\t'*indent + value)

    @abc.abstractmethod
    def add_axis(self, *args, **kwargs):
        axis = Axis(*name, **kwargs)
        self.axes.append(axis)

    @abc.abstractmethod
    def add_series(self, data, name=None, **kwargs):
        if not name:
            name = "Series%s" % (len(self.series) + 1)

    @property
    def javascript(self):
        script = []

        script.append("<script>")
        script.append("\tnv.addGraph(function() {")
        script.append("\t\tvar data=%s;" % json.dumps(self.series))
        script.append("\t\tvar chart = nv.models.%s();" % self._model)

        # allow hooks here

        for axis in self.axes:
            script.append('\t\tchart.%s' % axis.name)

            for attribute, value in axis.to_dict().items():
                script.append('\t\t\t.%s(%s)' % (attribute, value))

        script.append("\n\t\td3.select('#%s svg')" % self.element_id)
        script.append("\t\t.datum(data)")
        script.append("\t\t.call(chart);")

        script.append("\n\t\tnv.utils.windowResize(chart.update);")

        script.append("\n\t\treturn chart;")

        script.append("\n\t});")
        script.append("</script>")

        return '\n'.join(script)

    @property
    def html(self):
        return '<div id=%s><svg /></div>' % self.element_id


class Axis(object):

    def __init__(self, name, label=None, stagger_labels=False, rotate_labels=0,
        show_max_min=True, tick_format=None):
        self.name = name
        assert re.match('[xy][0-2]?Axis', name), \
            "Axis name must be one of 'xAxis', 'x1Axis', 'x2Axis', 'yAxis', 'y1Axis', 'y2Axis': %s" % name
        
        self.label = label
        self.stagger_labels = stagger_labels
        self.rotate_labels = rotate_labels
        self.show_max_min = show_max_min
        self.tick_format = tick_format

    def to_dict(self):
        """

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

        """

        # when creating a time format specifier in d3, 
        # there are a defined set of directives e.g. %a, %H, %Z, etc.
        # See: https://github.com/mbostock/d3/wiki/Time-Formatting
        directives = 'aAbBcdeHIjmMLpSUwWxXyYZ'
        pattern = '%%[%s]' % directives
        
        return bool(re.match(pattern, tick_format))