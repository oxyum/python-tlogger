# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class Event(object):
    fields_head = ('ts', 'level', 'id', 'guid', 'event', 'status',)
    fields_tail = ('raw',)

    def __init__(self, payload):
        self.payload = payload

    def items(self, omit=()):
        for field in self.fields_head:
            if field in self.payload and field not in omit:
                yield (field, self.payload[field])

        for field in sorted(set(self.payload) - set(self.fields_head)
                                              - set(self.fields_tail)):
            if field not in omit:
                yield (field, self.payload[field])

        for field in self.fields_tail:
            if field in self.payload and field not in omit:
                yield (field, self.payload[field])
