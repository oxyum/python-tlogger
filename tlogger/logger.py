# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .action_binder import ActionBinder
from .action_stack import action_stack
from .actions import Action
from .constants import Level
from .decorators import wrap_descriptor_method, wrap_function
from .proxies import ContextManagerProxy, IterableProxy
from .utils import is_descriptor


try:
    from django import VERSION  # nopep8
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False


class Logger(object):
    def __init__(self, name_or_logger, action_class=Action):
        self.logger = name_or_logger
        self.action_class = action_class

    def __call__(self, func=None, **kwargs):
        if func is None:
            return self.parametrized_decorator(**kwargs)

        return self._decorator(func, self.action_class, self.logger)

    if DJANGO_AVAILABLE:
        def view(self, func=None, **kwargs):
            params = self._get_view_defaults()
            if func is None:
                params.update(kwargs)
                return self.parametrized_decorator(**params)

            return self._decorator(func, self.action_class, self.logger,
                                   **params)

        def _get_view_defaults(self):
            return dict(hide_params=['result'])

    def parametrized_decorator(self, **kwargs):
        action_class = kwargs.pop('action_class', self.action_class)

        def decorator(func):
            return self._decorator(func, action_class, self.logger, **kwargs)

        return decorator

    def _decorator(self, func, action_class, logger, **kwargs):
        if is_descriptor(func):
            return wrap_descriptor_method(func, action_class, logger, **kwargs)

        return wrap_function(func, action_class, logger, **kwargs)

    def dump(self, **kwargs):
        self.event(suffix='dump_variable', payload=kwargs)

    def create_ad_hoc_action(self):
        return Action.create_ad_hoc(logger=self.logger)

    def event(self, suffix, payload, action=None, **kwargs):
        action = action or self.get_current_action()

        if action is None:
            with self.create_ad_hoc_action() as ad_hoc:
                ad_hoc.emit_event(suffix, payload, **kwargs)
        else:
            action.emit_event(suffix, payload, **kwargs)

    def get_current_action(self):
        return action_stack.peek()

    def start_action(self, name, **kwargs):
        return self.action_class(name, self.logger, **kwargs)

    def _raw(self, suffix, level, msg, *args, **kwargs):
        self.event(suffix, {}, level=level,
                   raw_msg=msg, raw_args=args, raw_kwargs=kwargs)

    def debug(self, msg, *args, **kwargs):
        self._raw('debug', Level.debug.value, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._raw('info', Level.info.value, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._raw('warning', Level.warning.value, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._raw('error', Level.error.value, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        exc_info = kwargs.pop('exc_info', 1)
        self._raw('exception', Level.error.value, msg, *args, exc_info=exc_info,
                  **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._raw('critical', Level.critical.value, msg, *args, **kwargs)

    def set_status(self, code, msg):
        self.get_current_action().set_status(code, msg)

    def action_for(self, func):
        return ActionBinder.get_action(func)

    def iter(self, iterable, steps=False, name=None, **kwargs):
        action = self.start_action(name or 'iterations', **kwargs)
        return IterableProxy(iterable, steps=steps, action=action)

    def context(self, context_manager, name=None, **kwargs):
        action = self.start_action(name or 'context', **kwargs)
        return ContextManagerProxy(context_manager, action=action)


def get_logger(name, logger_class=Logger):
    return logger_class(name)
