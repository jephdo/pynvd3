"""
    pynvd3._compat
    ~~~~~~~~~~~

    Some Python2/Python3 compatibility issues.
"""

import sys

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)
else:
    text_type = str
    string_types = (str,)
    integer_types = (int,)
