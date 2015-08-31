# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import time


class TLoggerFormatter(logging.Formatter):

    converter = time.gmtime
    FMT = "ts=%(asctime)s.%(msecs)dZ level=%(levelname)s %(message)s"
    DATEFMT = "%Y-%m-%dT%H:%M:%S"

    def __init__(self, fmt=None, datefmt=None):
        if fmt is None:
            fmt = self.FMT
        if datefmt is None:
            datefmt = self.DATEFMT
        super(TLoggerFormatter, self).__init__(fmt, datefmt)


class TLoggerLogRecord(logging.LogRecord):
    def getMessage(self):
        """
        Return the message for this LogRecord.

        Return the message for this LogRecord after merging any user-supplied
        arguments with the message.
        """
        if not logging._unicode: #if no unicode support...
            msg = str(self.msg)
        else:
            msg = self.msg
            if not isinstance(msg, basestring):
                try:
                    msg = str(self.msg)
                except UnicodeError:
                    msg = self.msg      #Defer encoding till later
        if self.args:
            msg = msg % tuple(
                '"{}"'.format(str(arg).encode('unicode_escape').decode())
                for arg in self.args
            )
        return msg


class TLoggerLogger(logging.Logger):
    """Yep, this is not what you think this is."""

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        rv = TLoggerLogRecord(name, level, fn, lno, msg, args, exc_info, func)
        if extra is not None:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in rv.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                rv.__dict__[key] = extra[key]
        return rv
