# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class KeyValueSerializer(object):
    def __init__(self, event, inline=()):
        self.event = event
        self.inline = inline

    def format_string(self):
        return ' '.join(
            '{}=%s'.format(k) if k not in self.inline else '{}={}'.format(k, v)
            for k, v in self.event.items()
        )

    def arguments(self):
        return [v for k, v in self.event.items(omit=self.inline)]
