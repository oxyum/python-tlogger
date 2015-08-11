# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock

from tlogger.events import Event


def test_event_items_ordered_manually():
    payload = {k: mock.Mock() for k in Event.fields_head}

    e = Event(payload=payload)

    assert [k for k, v in e.items()] == list(Event.fields_head)


def test_event_items_ordered_lexically():
    payload = {
        chr(i): mock.Mock()
        for i in range(ord('a'), ord('z'))
    }
    e = Event(payload=payload)

    keys = [k for k, v in e.items()]
    assert keys == sorted(keys)


def test_event_items_manual_before_random():
    payload = {k: mock.Mock() for k in ['a', 'b', 'raw', 'c', 'id']}

    e = Event(payload=payload)

    assert [k for k, v in e.items()] == ['id', 'a', 'b', 'c', 'raw']
