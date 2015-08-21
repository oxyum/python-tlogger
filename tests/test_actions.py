# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from tlogger.actions import Action
from tlogger.constants import Level


@pytest.fixture
def action(request, logger, action_stack):
    return Action('action_name', logger, action_stack=action_stack,
                  context_object=request.function)


@pytest.fixture
def logger():
    return mock.Mock()


@pytest.fixture
def action_stack():
    from tlogger.action_stack import ActionStack
    return ActionStack()


def test__action__create__defaults(logger):
    a = Action.create('name', logger,
                      context_object=test__action__create__defaults)
    assert a.name == 'name'
    assert a.logger is logger
    assert a.level == Level.info
    assert a.status_code == 0
    assert a.status_message == ''
    assert a.params == {}
    assert a.uid_field_name == 'id'
    assert a.uid is None


def test__action__create__level(logger):
    level = mock.Mock()
    a = Action.create('name', logger, level=level,
                      context_object=test__action__create__level)
    assert a.level is level


def test__action__create__id(logger):
    a = Action.create('name', logger, id='foobar',
                      context_object=test__action__create__id)
    assert a.uid == 'foobar'
    assert a.uid_field_name == 'id'


def test__action__create__guid(logger):
    a = Action.create('name', logger, guid='foobar',
                      context_object=test__action__create__guid)
    assert a.uid == 'foobar'
    assert a.uid_field_name == 'guid'


def test__action__create__uid(logger):
    a = Action.create('name', logger, uid='foobar',
                      context_object=test__action__create__uid)
    assert a.uid == 'foobar'
    assert a.uid_field_name == 'id'


def test__action__create__uid_field_name(logger):
    a = Action.create('name', logger, uid_field_name='foobar',
                      context_object=test__action__create__uid_field_name)
    assert a.uid is None
    assert a.uid_field_name == 'foobar'


def test__action__create__params(logger):
    params = mock.Mock()
    a = Action.create('name', logger, params=params,
                      context_object=test__action__create__params)
    assert a.params is params


def test__action__create__wrong_combination(logger):
    with pytest.raises(ValueError):
        Action.create('name', logger, id=1, guid=2)


def test__action__create_ad_hoc(logger):
    a = Action.create_ad_hoc(logger, context_object=test__action__create_ad_hoc)
    assert a.name == 'ad_hoc_action'
    assert a.logger is logger
    assert len(a.uid) == 36  # looks like a valid uuid4
    assert a.uid_field_name == 'guid'
    assert a.params == {}


def test__action__start__pushes_self_to_stack(action):
    with mock.patch.object(action, 'action_stack') as stack:
        action.start()

    stack.push.assert_called_once_with(action)


def test__action__start__emits_start_event(action):
    with mock.patch.object(action, 'emit_event') as emit_event:
        action.start()
    emit_event.assert_called_once_with('start', include_params=True)


def test__action__finish__pops_self_from_stack(action):
    with mock.patch.object(action, 'action_stack') as stack:
        action.finish()

    stack.pop.assert_called_once_with(action)


def test__action__finish__emits_finish_event(action):
    with mock.patch.object(action, 'emit_event') as emit_event:
        action.finish()
    emit_event.assert_called_once_with('finish', include_status=True)


def test__action__fail__pops_self_from_stack(action):
    with mock.patch.object(action, 'action_stack') as stack:
        action.fail()

    stack.pop.assert_called_once_with(action)


def test__action__fail__emits_failed_event(action):
    with mock.patch.object(action, 'emit_event') as emit_event:
        action.fail()
    emit_event.assert_called_once_with(
        'error',
        payload=None,
        include_status=True,
        trace_exception=False
    )


def test__action__fail__passes_exception_info(action):
    exc_type = mock.Mock()
    exc_val = mock.Mock()
    payload = {'exc_type': exc_type, 'exc_val': exc_val}
    with mock.patch.object(action, 'emit_event') as emit_event:
        action.fail(exc_type, exc_val)
    emit_event.assert_called_once_with(
        'error',
        payload=payload,
        include_status=True,
        trace_exception=False
    )


def test__action__emit_event_calls_log(action):
    with mock.patch.object(action, 'get_logger') as get_logger:
        action.emit_event('event')

    assert get_logger.return_value.log.call_count == 1
    assert get_logger.return_value.log.call_args[0][3] == \
           'test_actions.test__action__emit_event_calls_log.action_name.event'


def test__action__emit_event_calls_log_with_payload(action):
    with mock.patch.object(action, 'get_logger') as get_logger:
        action.emit_event('event', payload={'spam': 'eggs'})

    assert 'spam=%s' in get_logger.return_value.log.call_args[0][1]
    assert get_logger.return_value.log.call_args[0][4] == 'eggs'


def test__action__emit_event_calls_log_with_level(action):
    with mock.patch.object(action, 'get_logger') as get_logger:
        action.emit_event('event', level=Level.error)

    assert get_logger.return_value.log.call_args[0][0] == Level.error.value


def test__action__emit_event_calls_log_with_raw(action):
    with mock.patch.object(action, 'get_logger') as get_logger:
        action.emit_event('event', raw_msg='Aaaa! %s %s', raw_args=[1, 2])

    assert 'raw=Aaaa! %s %s' in get_logger.return_value.log.call_args[0][1]


def test__action__emit_event_calls_log_with_include_params(action):
    action.add_param(spam='eggs')

    with mock.patch.object(action, 'get_logger') as get_logger:
        action.emit_event('event', include_params=True)

    assert 'call_params=%s' in get_logger.return_value.log.call_args[0][1]


def test__action__emit_event_calls_log_with_include_status(action):
    with mock.patch.object(action, 'get_logger') as get_logger:
        action.emit_event('event', include_status=True)

    assert 'status_code=%' in get_logger.return_value.log.call_args[0][1]


def test__action__enter__calls_start_and_returns_self(action):
    with mock.patch.object(action, 'start') as start:
        assert action.__enter__() is action
        start.assert_called_once_with()


def test__action__exit__calls_finish(action):
    with mock.patch.object(action, 'finish') as finish:
        action.__exit__(None, None, None)
    finish.assert_called_once_with()


def test__action__exit__calls_fail(action):
    exc_type, exc_val, exc_tb = Exception, Exception('Waaagh!'), mock.Mock()
    with mock.patch.object(action, 'fail') as fail:
        action.__exit__(exc_type, exc_val, exc_tb)
    fail.assert_called_once_with(exc_type, exc_val, exc_tb)
