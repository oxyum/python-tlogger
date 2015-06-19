# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from logging import getLogger, basicConfig
from uuid import uuid4


def create_logger(name):
    basicConfig(level=0)
    logger = getLogger(name)
    return logger


def create_guid():
    return str(uuid4())


def is_descriptor(obj):
    if (
        hasattr(obj, '__get__') or
        hasattr(obj, '__set__') or
        hasattr(obj, '__delete__')
    ):
            return True
    return False
