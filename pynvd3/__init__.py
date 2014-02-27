try:
    import pandas as pd
except ImportError:
    PANDAS_INSTALLED = False
else:
    PANDAS_INSTALLED = True

from .charts import *