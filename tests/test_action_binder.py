# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def test_empty(action_binder):
    assert action_binder.get_action(object()) is None


def test_bind(action_binder, function):
    a = object()
    action_binder.bind(function, a)
    assert action_binder.get_action(function) is a


def test_unbind(action_binder, function):
    a = object()
    action_binder.bind(function, a)
    action_binder.unbind(function)
    assert action_binder.get_action(function) is None


def test_context_normal_exit(action_binder):
    a = action_binder.action
    f = action_binder.func
    assert action_binder.get_action(f) is None
    with action_binder:
        assert action_binder.get_action(f) is a
    assert action_binder.get_action(f) is None


def test_context_error(action_binder):
    a = action_binder.action
    f = action_binder.func
    assert action_binder.get_action(f) is None
    try:
        with action_binder:
            assert action_binder.get_action(f) is a
            1 / 0
    except ZeroDivisionError:
        pass
    assert action_binder.get_action(f) is None


def test_enter(action_binder):
    assert action_binder.__enter__() is action_binder
    assert action_binder.get_action(action_binder.func) is action_binder.action


def test_exit(action_binder):
    assert action_binder.__enter__() is action_binder
    action_binder.__exit__(None, None, None)
    assert action_binder.get_action(action_binder.func) is None
