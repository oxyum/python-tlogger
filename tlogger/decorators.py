# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps
import inspect

from .action_binder import ActionBinder


def wrap_function(func, action_class, logger, **params):
    """
    Wrap function into an action.

    :param func: a callable to wrap
    :type func: function

    :param action_class: a class of action to wrap function into
    :type action_class: type

    :param logger: Logger object or name to write messages to
    :type logger: Logger | str

    :param params: additional parameters to be passed to action
    :type params: dict

    :return: wrapping function
    :rtype: function
    """
    action_name = (
        params.pop('action_name', None) or
        getattr(func, '__name__', None) or
        getattr(func.__class__, '__name__')
    )

    @wraps(func)
    def decorator(*args, **kwargs):
        action = action_class(name=action_name, logger=logger, **params)
        func_call_params = inspect.getcallargs(func, *args, **kwargs)

        if func_call_params:
            action.add_params(func_call_params)

        with action:
            with ActionBinder(decorator, action):
                result = func(*args, **kwargs)

            action.add_result(result)
            return result

    return decorator


def wrap_descriptor_method(descriptor, action_class, logger, **params):
    class DescriptorProxy(object):
        def __get__(self, instance, owner):
            func = descriptor.__get__(instance, owner)
            if callable(func):
                return wrap_function(func, action_class, logger, **params)
            return func

        def __call__(self, *args, **kwargs):
            return (
                wrap_function(descriptor, action_class, logger, **params)
                (*args, **kwargs)
            )

        def __getattr__(self, item):
            return getattr(descriptor, item)

    return DescriptorProxy()
