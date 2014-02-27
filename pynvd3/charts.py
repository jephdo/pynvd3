"""
    nvd3.charts
    ~~~~~~~~~~~

    Charts that can be produced with pynvd3. Vist the NVD3 
    `example page <http://nvd3.org/ghpages/examples.html>`_ for a better feel
    for what charts are available.
"""

from .base import AbstractNvd3Chart


class LineChart(AbstractNvd3Chart):
    _model = 'lineChart'

    def add_axis(self, *args, **kwargs):
        super().add_axis(*args, **kwargs)

    def add_series(self, *args, **kwargs):
        super().add_series(*args, **kwargs)


class MultiBarChart(AbstractNvd3Chart):
    _model = 'multiBarChart'


class DiscreteBarChart(AbstractNvd3Chart):
    _model = 'discreteBarChart'


class StackedAreaChart(AbstractNvd3Chart):
    _model = 'stackedAreaChart'


class MultiBarHorizontalChart(AbstractNvd3Chart):
    _model = 'multiBarHorizontalChart'

