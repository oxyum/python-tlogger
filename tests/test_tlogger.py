# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import tlogger


def test_get_logger_decorator():
    use_logger = tlogger.get_logger_decorator(__name__)
    assert callable(use_logger)
