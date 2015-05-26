# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import wraps

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
    action_name = params.pop('action_name', func.__name__)

    @wraps(func)
    def decorator(*args, **kwargs):
        action = action_class(name=action_name, logger=logger, **params)
        action.add_args(*args)
        action.add_kwargs(**kwargs)

        with action:
            with ActionBinder(decorator, action):
                result = func(*args, **kwargs)

            action.add_result(result)
            return result

    return decorator


