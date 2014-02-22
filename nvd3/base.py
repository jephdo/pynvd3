"""
    nvd3.base
    ~~~~~~~~~~~

    Base classes and objects for constructing charts. Each chart type should 
    inherit from :class:`AbstractNvd3Chart` and implement the necessary
    constructor methods.
"""

import abc

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
        self.axes = {}
        self.javascript = []

    # def write(self, value, indent=0):
    #     self.javascript.append('\t'*indent + value)

    @abc.abstractmethod
    def add_axis(self, *args, **kwargs):
        pass

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
    _tick_format = 
    _
    def __init__(self, )

