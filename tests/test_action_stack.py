# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest


@pytest.fixture
def action_stack():
    from tlogger.action_stack import ThreadLocalActionStack
    return ThreadLocalActionStack()


def test_empty(action_stack):
    assert action_stack.peek() is None
    assert action_stack.root() is None


def test_push_single(action_stack):
    a = object()
    action_stack.push(a)
    assert action_stack.peek() is a
    assert action_stack.root() is a


def test_push_multiple(action_stack):
    a = object()
    b = object()
    c = object()
    action_stack.push(a)
    action_stack.push(b)
    action_stack.push(c)
    assert action_stack.peek() is c
    assert action_stack.root() is a


def test_pop_single(action_stack):
    a = object()
    action_stack.push(a)
    action_stack.pop()
    assert action_stack.peek() is None
    assert action_stack.root() is None


def test_pop_multiple(action_stack):
    a = object()
    b = object()
    c = object()
    action_stack.push(a)
    action_stack.push(b)
    action_stack.push(c)
    action_stack.pop()
    action_stack.pop()
    action_stack.pop()
    assert action_stack.peek() is None
    assert action_stack.root() is None


def test_pop_restricted(action_stack):
    a = object()
    b = object()
    c = object()
    action_stack.push(a)
    action_stack.push(b)
    action_stack.push(c)
    action_stack.pop(c)
    assert action_stack.peek() is b
    assert action_stack.root() is a
    action_stack.pop(a)
    assert action_stack.peek() is b
    assert action_stack.root() is a


def test_thread_start(action_stack):
    """
    Each thread starts with an empty action stack.
    """
    from threading import Thread

    first = object()
    action_stack.push(first)

    values_in_thread = []

    def in_thread():
        values_in_thread.append(action_stack.peek())

    thread = Thread(target=in_thread)
    thread.start()
    thread.join()
    assert values_in_thread == [None]


def test_thread_safety(action_stack):
    """
    Each thread gets its own action stack.
    """
    from threading import Thread

    first = object()
    action_stack.push(first)

    second = object()
    values_in_thread = []

    def in_thread():
        action_stack.push(second)
        values_in_thread.append(action_stack.peek())

    thread = Thread(target=in_thread)
    thread.start()
    thread.join()
    # Neither thread was affected by the other:
    assert values_in_thread == [second]
    assert action_stack.peek() is first
