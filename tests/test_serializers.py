# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from tlogger.events import Event
from tlogger.serializers import KeyValueSerializer


def test_format_string():
    event = Event({'foo': 1})
    serializer = KeyValueSerializer(event)
    assert serializer.format_string() == 'foo=%s'


def test_format_string_inline():
    event = Event({'foo': 1, 'bar': 2})
    serializer = KeyValueSerializer(event, inline=['bar'])
    assert serializer.format_string() == 'bar=2 foo=%s'


def test_arguments():
    event = Event({'foo': 1})
    serializer = KeyValueSerializer(event)
    assert serializer.arguments() == [1]


def test_arguments_inline():
    event = Event({'foo': 1, 'bar': 2})
    serializer = KeyValueSerializer(event, inline=['bar'])
    assert serializer.arguments() == [1]
