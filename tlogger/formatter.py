# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time


class TLoggerFormatter(logging.Formatter):

    converter = time.gmtime
    FMT = "ts=%(asctime)s.%(msecs)dZ level=%(levelname)s %(message)s"
    DATEFMT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = self.FMT
        if datefmt is None:
            datefmt = self.DATEFMT
        super(TLoggerFormatter, self).__init__(fmt, datefmt)
