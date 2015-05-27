# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings

from ..action_binder import ActionBinder
from ..actions import Action


class ActionMiddleware(object):
    header = getattr(settings, 'TLOGGER_REQUEST_ID_HEADER_NAME',
                     'HTTP_REQUEST_ID')
    action_name = getattr(settings, 'TLOGGER_REQUEST_ACTION_NAME', 'request')
    logger = getattr(settings, 'TLOGGER_REQUEST_LOGGER', 'tlogger.request')

    def __init__(self, action_class=Action):
        self.action_class = action_class

    def process_request(self, request):
        action = self.action_class.create(
            self.action_name,
            self.logger,
            guid=(request.META.get(self.header))
        )
        ActionBinder.bind(request, action)
        action.start()

    def process_response(self, request, response):
        action = ActionBinder.get_action(request)
        if action is not None:
            action.finish()
            ActionBinder.unbind(request)
        return response
