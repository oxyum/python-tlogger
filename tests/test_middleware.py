# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest

from tlogger.action_binder import ActionBinder


@pytest.fixture
def http_request():
    return mock.Mock(
        spec=[],
        POST={},
        GET={},
        META={'HTTP_REQUEST_ID': 'deadbeef'}
    )


@pytest.fixture
def action_middleware():
    from tlogger.django.middleware import ActionMiddleware
    return ActionMiddleware(mock.Mock())


def test__process_request__starts_action(http_request, action_middleware):
    assert action_middleware.process_request(http_request) is None
    assert ActionBinder.get_action(http_request) is not None

    action_middleware.action_class.create.assert_called_once_with(
        action_middleware.action_name,
        action_middleware.logger,
        guid=http_request.META['HTTP_REQUEST_ID']
    )
    action = action_middleware.action_class.create.return_value
    action.start.assert_called_once_with()


def test__process_response__finishes_action(http_request, action_middleware):
    response = mock.Mock()
    action = mock.Mock()
    ActionBinder.bind(http_request, action)

    result = action_middleware.process_response(http_request, response)
    assert result is response
    action.finish.assert_called_once_with()


def test__process_response__wo_action(http_request, action_middleware):
    response = mock.Mock()
    result = action_middleware.process_response(http_request, response)
    assert result is response
