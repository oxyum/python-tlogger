# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys


PY3 = sys.version[0] == '3'
if PY3:
    string_types = (str,)
else:
    string_types = (str, unicode)
