# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class BaseProxy(object):
    def __init__(self, obj, action=None):
        self._wrapped = obj
        self._action = action

    def __getattr__(self, item):
        return getattr(self._wrapped, item)


class IterableProxy(BaseProxy):
    # TODO: support for coroutines, those things with .send()
    def __init__(self, obj, action, steps=False):
        super(IterableProxy, self).__init__(obj, action)
        self._iterator = iter(obj)
        self._steps = steps
        self._count = 0
        self._started = False
        self._finished = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self._started:
            self._action.start()
            self._started = True

        try:
            value = next(self._iterator)
            if self._steps:
                self._action.emit_event(
                    'step',
                    {'value': value, 'step': self._count}
                )
            self._count += 1
            return value
        except StopIteration:
            if not self._finished:
                self._action.finish()
                self._finished = True
            raise

    next = __next__


class ContextManagerProxy(BaseProxy):
    def __enter__(self):
        self._action.add_param(obj=self._wrapped)
        self._action.start('enter')

        self._wrapped.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._wrapped.__exit__(exc_type, exc_val, exc_tb)

        if exc_val is None:
            self._action.finish('exit')
        else:
            self._action.fail(exc_type, exc_val, exc_tb,
                              event_name='exit_with_error')
