# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from tlogger.constants import Level


MOD_PATH = 'tlogger.logger'


@pytest.fixture
def logger():
    return mock.Mock()


@pytest.fixture
def tlogger(logger):
    from tlogger.logger import Logger
    return Logger(logger)


def test__logger__call__wraps_function_wo_params(tlogger):
    def func(arg1, arg2):
        return arg1 + arg2

    with mock.patch('%s.wrap_descriptor_method' % MOD_PATH) as wrap_function:
        tlogger(func)

    wrap_function.assert_called_once_with(func, tlogger.action_class,
                                          tlogger.logger)


def test__logger__call__wraps_function_with_params(tlogger):
    def func(arg1, arg2):
        return arg1 + arg2

    params = {'spam': 'eggs'}

    with mock.patch('%s.wrap_descriptor_method' % MOD_PATH) as wrap_function:
        tlogger(params=params)(func)

    wrap_function.assert_called_once_with(func, tlogger.action_class,
                                          tlogger.logger, params=params)


def test__logger__dump__calls_event(tlogger):
    with mock.patch.object(tlogger, 'event') as event:
        tlogger.dump(spam='eggs')
    event.assert_called_once_with(suffix='dump_variable',
                                  payload={'spam': 'eggs'})


def test__logger__event__creates_ad_hoc_action(tlogger):
    with mock.patch.object(tlogger, 'create_ad_hoc_action') as create_ad_hoc:
        tlogger.event('bang', {})

    create_ad_hoc.assert_called_once_with()
    create_ad_hoc.return_value.__enter__.assert_called_once_with()
    ad_hoc = create_ad_hoc.return_value.__enter__.return_value
    ad_hoc.emit_event.assert_called_once_with('bang', {})
    create_ad_hoc.return_value.__exit__.assert_called_once_with(None, None, None)


def test__logger__event__calls_emit_event_on_current_action(tlogger):
    with mock.patch.object(tlogger, 'get_current_action') as get_current_action:
        tlogger.event('spam', {})

    get_current_action.return_value.emit_event.assert_called_once_with(
        'spam', {})


def test__logger__event__calls_emit_event_on_given_action(tlogger):
    action = mock.MagicMock()
    tlogger.event('eggs', {}, action=action)
    action.emit_event.assert_called_once_with('eggs', {})


def test__logger__create_ad_hoc_action__returns_action(tlogger):
    action = tlogger.create_ad_hoc_action()
    assert action.logger is tlogger.logger
    assert action.name == 'ad_hoc_action'


def test__logger__start_action__returns_action(tlogger):
    action = tlogger.start_action('new-action-name')
    assert action.name == 'new-action-name'
    assert action.__class__ is tlogger.action_class
    assert action.logger is tlogger.logger


def test__logger__raw__calls_event(tlogger):
    suffix = 'bdysch!'
    level = 20
    message = 'something fell'
    with mock.patch.object(tlogger, 'event') as event:
        tlogger._raw(suffix, level, message)

    event.assert_called_once_with(suffix, {}, level=level, raw_msg=message,
                                  raw_args=(), raw_kwargs={})


def test__logger__debug__calls_raw(tlogger):
    msg = 'Aaaa!'
    with mock.patch.object(tlogger, '_raw') as raw:
        tlogger.debug(msg)
    raw.assert_called_once_with('debug', Level.debug, msg)


def test__logger__info__calls_raw(tlogger):
    msg = 'Aaaa!'
    with mock.patch.object(tlogger, '_raw') as raw:
        tlogger.info(msg)
    raw.assert_called_once_with('info', Level.info, msg)


def test__logger__warning__calls_raw(tlogger):
    msg = 'Aaaa!'
    with mock.patch.object(tlogger, '_raw') as raw:
        tlogger.warning(msg)
    raw.assert_called_once_with('warning', Level.warning, msg)


def test__logger__error__calls_raw(tlogger):
    msg = 'Aaaa!'
    with mock.patch.object(tlogger, '_raw') as raw:
        tlogger.error(msg)
    raw.assert_called_once_with('error', Level.error, msg)


def test__logger__critical__calls_raw(tlogger):
    msg = 'Aaaa!'
    with mock.patch.object(tlogger, '_raw') as raw:
        tlogger.critical(msg)
    raw.assert_called_once_with('critical', Level.critical, msg)


def test__logger__set_status__delegates_to_current_action(tlogger):
    code = 235
    msg = 'Nuclear disaster'
    with mock.patch.object(tlogger, 'get_current_action') as get_current_action:
        tlogger.set_status(code, msg)

    get_current_action.return_value.set_status.assert_called_once_with(
        code, msg)


def test__logger__action_for__returns_bound_action(tlogger):
    from tlogger.action_binder import ActionBinder

    action = mock.Mock()
    func = mock.Mock()
    ActionBinder.bind(func, action)

    assert tlogger.action_for(func) is action


def test__logger__iter__returns_iterable_proxy(tlogger):
    orig = range(5)
    proxy = tlogger.iter(orig)
    assert list(proxy) == list(range(5))
    assert proxy._wrapped is orig
    assert proxy._action.name == 'iterations'


def test__logger__context__returns_context_manager_proxy(tlogger):
    real = mock.MagicMock()
    with tlogger.context(real):
        real.__enter__.called_once_with()
    real.__exit__.assert_called_once_with(None, None, None)


def test__get_logger__returns_logger():
    from tlogger.logger import get_logger

    name = 'logger.name'
    logger = get_logger(name)
    assert logger.logger == name
