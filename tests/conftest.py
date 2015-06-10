# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from django.conf import settings


def pytest_configure():
    settings.configure()


@pytest.fixture
def action_binder(function):
    from tlogger.action_binder import ActionBinder
    return ActionBinder(function, mock.Mock())


@pytest.fixture
def function():
    def identity(arg):
        return arg
    return identity
