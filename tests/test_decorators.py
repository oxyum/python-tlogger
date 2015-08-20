# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock

from tlogger.decorators import wrap_function


def test_returns_callable(function):
    assert callable(wrap_function(function, mock.Mock(), mock.Mock()))


def test_wrapped_name_equals_function_name(function):
    wrapped = wrap_function(function, mock.Mock(), mock.Mock())
    assert function.__name__ == wrapped.__name__


def test_wrapped_returns_function_result(function):
    wrapped = wrap_function(function, mock.MagicMock(), mock.Mock())
    result = wrapped(1)
    assert result == function(1)


def test_wrapped_calls_action_class(function):
    action_class = mock.MagicMock()
    logger = mock.Mock()
    wrap_function(function, action_class, logger)(1)
    assert action_class.called_once_with(name=function.__name__, logger=logger)


def test_action_name_override(function):
    name = 'my.action.name'
    action_class = mock.MagicMock()
    logger = mock.Mock()
    wrap_function(function, action_class, logger, action_name=name)(1)
    assert action_class.called_once_with(name=name, logger=logger)


def test_activates_action_context(function):
    action_class = mock.MagicMock()
    logger = mock.Mock()
    wrap_function(function, action_class, logger)(1)
    action = action_class.return_value
    action.__enter__.assert_called_once_with()
    action.__exit__.assert_called_once_with(None, None, None)
