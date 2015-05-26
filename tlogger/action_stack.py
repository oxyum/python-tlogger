# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import threading


class ActionStack(object):
    def __init__(self):
        self._stack = []

    def push(self, action):
        self._stack.append(action)

    def pop(self, action=None):
        if action is None:
            return self._stack.pop()

        if action is self.peek():
            return self._stack.pop()

    def peek(self):
        if not self._stack:
            return None

        return self._stack[-1]

    def root(self):
        if not self._stack:
            return None

        return self._stack[0]


class ThreadLocalActionStack(threading.local, ActionStack):
    pass


action_stack = ThreadLocalActionStack()
