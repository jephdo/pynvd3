"""
    pynvd3.charts
    ~~~~~~~~~~~

    Charts that can be produced with pynvd3. Vist the NVD3 
    `example page <http://nvd3.org/ghpages/examples.html>`_ for a better feel
    for what charts are available.
"""

from .base import AbstractNvd3Chart


class _Nvd3Chart(AbstractNvd3Chart):

    def add_axis(self, *args, **kwargs):
        super(_Nvd3Chart, self).add_axis(*args, **kwargs)

    def add_series(self, *args, **kwargs):
        super(_Nvd3Chart, self).add_series(*args, **kwargs)


class LineChart(_Nvd3Chart):
    _model = 'lineChart'


class MultiBarChart(_Nvd3Chart):
    _model = 'multiBarChart'


class DiscreteBarChart(_Nvd3Chart):
    _model = 'discreteBarChart'


class StackedAreaChart(_Nvd3Chart):
    _model = 'stackedAreaChart'


class MultiBarHorizontalChart(_Nvd3Chart):
    _model = 'multiBarHorizontalChart'
