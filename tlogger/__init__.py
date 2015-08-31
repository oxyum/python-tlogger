# -*- mode: python; coding: utf-8; -*-

from .augments import TLoggerFormatter, TLoggerLogger as _Logger  # nopep8
from .logger import get_logger  # nopep8


import logging as _logging

_logging.basicConfig(level=0)
_logging.setLoggerClass(_Logger)
