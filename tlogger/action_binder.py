# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class ActionBinder(object):
    attribute_name = '_action'

    def __init__(self, func, action):
        self.func = func
        self.action = action

    def __enter__(self):
        self.bind(self.func, self.action)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind(self.func)

    @classmethod
    def bind(cls, func, action):
        setattr(func, cls.attribute_name, action)

    @classmethod
    def unbind(cls, func):
        delattr(func, cls.attribute_name)

    @classmethod
    def get_action(cls, func):
        return getattr(func, cls.attribute_name, None)
