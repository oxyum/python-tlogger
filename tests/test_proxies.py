# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest


@pytest.fixture
def action():
    from tlogger.actions import Action
    return mock.Mock(spec=Action)


@pytest.fixture
def iterable_proxy(action):
    from tlogger.proxies import IterableProxy
    return IterableProxy(range(3), action)


@pytest.fixture
def iterable_proxy_raise(action):
    from tlogger.proxies import IterableProxy

    def iterable():
        for i in range(3):
            if i == 1:
                raise Exception('Whoa!')
            yield i

    return IterableProxy(iterable(), action)


@pytest.fixture
def iterable_proxy_steps(action):
    from tlogger.proxies import IterableProxy
    return IterableProxy(range(3), action, steps=True)


@pytest.fixture
def ctxmgr_proxy(action):
    from tlogger.proxies import ContextManagerProxy
    return ContextManagerProxy(mock.MagicMock(), action)


def test_iterable_proxy_wo_steps(action, iterable_proxy):
    assert list(iterable_proxy) == [0, 1, 2]

    action.start.assert_called_once_with()
    action.finish.assert_called_once_with()


def test_iterable_proxy_with_steps(action, iterable_proxy_steps):
    assert list(iterable_proxy_steps) == [0, 1, 2]

    action.start.assert_called_once_with()
    action.finish.assert_called_once_with()
    assert action.emit_event.call_count == 3


def test_iterable_proxy_attributes(action, iterable_proxy):
    real = iterable_proxy._wrapped

    for attr in dir(real):
        if attr.startswith('_'):
            continue

        assert getattr(iterable_proxy, attr) == getattr(real, attr)


def test_iterable_proxy_interrupted(action, iterable_proxy):
    assert action.start.call_count == 0
    assert action.finish.call_count == 0

    yielded = []

    # make a couple if steps and stop
    for i, n in enumerate(iterable_proxy):
        yielded.append(n)
        if i == 1:
            break

    assert yielded == [0, 1]
    assert action.start.call_count == 1
    assert action.finish.call_count == 0

    # loop all the rest
    for i, n in enumerate(iterable_proxy):
        yielded.append(n)

    assert yielded == [0, 1, 2]
    assert action.start.call_count == 1
    assert action.finish.call_count == 1

    # ensure nothing changes if we try to loop over an exhausted iterable
    for i, n in enumerate(iterable_proxy):
        yielded.append(n)

    assert yielded == [0, 1, 2]
    assert action.start.call_count == 1
    assert action.finish.call_count == 1


def test_iterable_proxy_raises_exception(iterable_proxy_raise):
    with pytest.raises(Exception):
        for _ in iterable_proxy_raise():
            pass


def test_context_manager_proxy_attributes(ctxmgr_proxy):
    for attr in dir(ctxmgr_proxy):
        if attr.startswith('_'):
            continue

        assert getattr(ctxmgr_proxy, attr) == \
               getattr(ctxmgr_proxy._wrapped, attr)


def test_context_manager_proxy_calls_start_and_finish(action, ctxmgr_proxy):
    assert action.start.call_count == 0
    assert action.finish.call_count == 0
    assert action.fail.call_count == 0

    with ctxmgr_proxy:
        assert action.start.call_count == 1
        assert action.finish.call_count == 0
        assert action.fail.call_count == 0

    assert action.start.call_count == 1
    assert action.finish.call_count == 1
    assert action.fail.call_count == 0


def test_context_manager_proxy_calls_start_and_fail(action, ctxmgr_proxy):
    assert action.start.call_count == 0
    assert action.finish.call_count == 0
    assert action.fail.call_count == 0

    with pytest.raises(Exception):
        with ctxmgr_proxy:
            assert action.start.call_count == 1
            assert action.finish.call_count == 0
            assert action.fail.call_count == 0

            raise Exception('Bang!')

    assert action.start.call_count == 1
    assert action.finish.call_count == 0
    assert action.fail.call_count == 1
