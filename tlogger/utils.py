# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from logging import getLogger, basicConfig
from uuid import uuid4


def create_ts():
    return datetime.utcnow()


def create_logger(name):
    basicConfig(level=0)
    logger = getLogger(name)
    return logger


def create_guid():
    return str(uuid4())
