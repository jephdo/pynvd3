
#pynvd3: A Python wrapper for NVD3.js

[NVD3.js](http://nvd3.org/) is a charting library built on top of the javascript library [D3.js](http://d3js.org/). *pynvd3* allows you to produce the javascript required to display charts using only Python.


Installation
-------------
```shell
$ pip install pynvd3
```

Optional Dependencies
---------------------
ujson
pandas


Examples
--------
Let's plot a sin curve:

```python
>>> from math import sin
>>> from nvd3 import LineChart
>>> x_values = list(n*0.1 for n in range(0,80))
>>> y_values = [sin(x) for x in x_values]
>>> cht = LineChart()
>>> cht.add_series(x_values, y_values)
>>> cht.script

```

Vist the NVD3 [example page](http://nvd3.org/ghpages/examples.html) for a better idea of what charts are available.


Usage with pandas
------------------
[pandas](http://pandas.pydata.org/) is a Python library containing "high-performance, easy-to-use data structures and data analysis tools". *pynvd3* is a personal project used to generate NVD3 charts from directly from *pandas* datastructures.

Within the library, there exist a few tools to help translate DataFrames and Series into appropriate charts.

The list of values in the index of a `DataFrame` (or `Series`) always becomes the values of the x-coordinates:


This also goes for indexes that are of type `DatetimeIndex` i.e. time series data:

It is also possible to just directly feed in a `DataFrame`:

