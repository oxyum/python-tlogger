# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import inspect

from qualname import qualname


def find_qualified_name(obj):
    name = None

    try:
        name = qualname(obj)
    except (AttributeError, IOError):
        pass

    if name is None:
        try:
            name = obj.__name__
        except AttributeError:
            pass

    if name is None:
        name = repr(obj)

    module = inspect.getmodule(obj)

    return '.'.join(filter(None, (getattr(module, '__name__', ''), name)))
