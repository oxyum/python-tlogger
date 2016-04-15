# -*- mode: python; coding: utf-8; -*-
import logging
import time
from collections import OrderedDict
from inspect import getcallargs
from functools import partial

from tlogger.method_decorator import method_decorator


CALLABLE_ARG_PREFIX = "callable_arg__"


class TLoggerFormatter(logging.Formatter):

    converter = time.gmtime
    FMT = "ts=%(asctime)s.%(msecs)03dZ level=%(levelname)s %(message)s"

    DATEFMT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = TLoggerFormatter.FMT
        if datefmt is None:
            datefmt = TLoggerFormatter.DATEFMT
        logging.Formatter.__init__(self, fmt, datefmt)


class TLogger(object):

    def __init__(self, event_prefix, logger_name=None, fail_silently=True):
        self.event_prefix = event_prefix
        self.needs_event_end = True

        if logger_name is None:
            logger_name = __name__

        self._logger = logging.getLogger(logger_name)
        self._params = {}
        self.fail_silently = fail_silently

    @staticmethod
    def _make_message(data):
        parts = []

        for k, v in OrderedDict(sorted(data.items(), key=lambda t: t[0])).items():
            value = v
            if isinstance(value, basestring):
                value = value.replace('"', r'\"')

            if k == "event":
                parts.insert(0, '%s="%s"' % (k, value))
            else:
                parts.append('%s="%s"' % (k, value))

        return " ".join(parts)

    def _event_logger_error(self):
        data = {}
        data["event"] = "tlogger.exception"
        data["original_event"] = self.event_prefix
        data["status"] = "-1"

        data_with_params = data.copy()
        data_with_params.update(self._params)

        try:
            self._logger.warning(TLogger._make_message(data_with_params))
        except:
            data["msg"] = "Can't serialize params"
            self._logger.warning(TLogger._make_message(data))

    def add_params(self, *args, **kwargs):

        if args:
            params = args[0]
        elif "params" in kwargs:
            params = kwargs.get("params")
        else:
            params = kwargs

        try:
            self._params.update(params)
        except:
            if self.fail_silently:
                self._event_logger_error()
            else:
                raise

    def event(self, name=None, level='INFO', status=None, **kwargs):
        try:
            data = self._params.copy()
            data.update(kwargs)

            event_name = self.event_prefix
            if name is not None:
                event_name = "%s.%s" % (event_name, name)
            data["event"] = event_name

            if status is not None:
                data["status"] = status

            LEVEL = logging.getLevelName(level)
            if self._logger.isEnabledFor(LEVEL):
                self._logger._log(LEVEL, TLogger._make_message(data), tuple())
        except:
            if self.fail_silently:
                self._event_logger_error()
            else:
                raise

    def event_start(self, **kwargs):
        self.event(name="start", **kwargs)

    def event_end(self, status=0, **kwargs):
        self.event(name="end", status=status, **kwargs)
        self.needs_event_end = False

    def event_error(self, status=None, **kwargs):
        if status in ("0", 0):
            raise ValueError("Error status can't be equal to 0")
        if status is None:
            status = -1
        self.event(name="error", status=status, **kwargs)
        self.needs_event_end = False


def _get_event_prefix(dec):
    pieces = [dec.__module__]
    if dec.cls:
        pieces.append(dec.cls.__name__)
    pieces.append(dec.__name__)
    return ".".join(pieces)


def _construct_params_to_add(callargs, func_args, ignore):
    if ignore is None:
        ignore = []

    if func_args is None:
        func_args = {}

    result = {}
    for arg, value in callargs.iteritems():
        if arg in ignore:
            continue
        if arg not in func_args:
            result[CALLABLE_ARG_PREFIX + arg] = value
        else:
            param = func_args[arg]
            if isinstance(param, basestring):
                result[param] = value
            else:
                name, attr = param
                result[name] = getattr(value, attr, "")
    return result


def use_logger(function=None,
               no_start_event=False,
               no_end_event=False,
               func_args=None,
               ignore=None,
               special_args=None,
               logger_var="logger",
               logger_class=None,
               logger_name=None):

    class actual_decorator(method_decorator):
        def __call__(self, *args, **kwargs):

            need_restore = False
            if logger_var in self.func.func_globals:
                need_restore = True
                old = self.func.func_globals[logger_var]

            if logger_class is None:
                _logger_class = TLogger
            else:
                _logger_class = logger_class

            logger = _logger_class(_get_event_prefix(self), logger_name)
            self.func.func_globals[logger_var] = logger

            callargs = getcallargs(self.func, *args, **kwargs)
            params_to_add = _construct_params_to_add(
                callargs, func_args, ignore
            )
            logger.add_params(params_to_add)

            if special_args is not None:
                logger.add_special_args(special_args)

            if not no_start_event:
                logger.event_start()

            result = method_decorator.__call__(self, *args, **kwargs)

            if need_restore:
                self.func.func_globals[logger_var] = old
            else:
                del self.func.func_globals[logger_var]

            if not no_end_event and logger.needs_event_end:
                logger.event_end()

            return result

    if function is not None:
        return actual_decorator(function)

    return actual_decorator


def get_logger_decorator(logger_name):
    return partial(use_logger, logger_name=logger_name)
