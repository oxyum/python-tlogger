# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from itertools import chain

from .action_stack import action_stack
from .compat import string_types
from .constants import INFO
from .events import Event
from .serializers import KeyValueSerializer
from .utils import create_ts, create_logger, create_guid


class Action(object):
    CLEANSED_SUBSTITUTE = '******'

    def __init__(self, name, logger, level=INFO, uid=None, uid_field_name='id',
                 params=None, action_stack=action_stack, sensitive_params=None,
                 hide_params=None):

        self.name = name
        self.logger = logger
        self.level = level

        self.status_code = 0
        self.status_message = ''
        self.params = params or {}

        self.uid_field_name = uid_field_name
        self.uid = uid

        self.action_stack = action_stack
        self.sensitive_params = sensitive_params or ()
        self.hide_params = hide_params or ()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            self.finish()
        else:
            self.fail(exc_type, exc_val, exc_tb)

    def __repr__(self):
        return str(
            'Action({name!r}, {logger!r}, level={level!r}, uid={uid!r}, '
            'uid_field_name={uid_field_name!r}, params={params!r}, '
            'action_stack={action_stack!r})'
            .format(**vars(self))
        )

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return '<Action %s>' % self.name

    @classmethod
    def create(cls, name, logger, level=INFO, id=None, guid=None, uid=None,
               uid_field_name='id', params=None, sensitive_params=None,
               hide_params=None):

        assert len(list(filter(lambda x: x is None, [id, uid, guid]))) >= 2,\
               'id, uid and guid arguments are mutually exclusive'

        if id is not None:
            uid_field_name, uid = 'id', id
        elif guid is not None:
            uid_field_name, uid = 'guid', guid

        return cls(name, logger, level=level, uid=uid,
                   uid_field_name=uid_field_name, params=params,
                   sensitive_params=sensitive_params, hide_params=hide_params)

    @classmethod
    def create_ad_hoc(cls, logger, params=None):
        uid_field_name, uid = cls.generate_uid_tuple()
        return cls(
            name='ad_hoc_action',
            logger=logger,
            uid_field_name=uid_field_name, uid=uid,
            params=params,
        )

    @classmethod
    def generate_uid_tuple(cls):
        return 'guid', create_guid()

    def start(self, event_name='start'):
        self.action_stack.push(self)
        self.emit_event(event_name, include_params=True)

    def finish(self, event_name='finish'):
        self.emit_event(event_name, include_status=True)
        self.action_stack.pop(self)

    def fail(self, exc_type=None, exc_val=None, exc_tb=None,
             event_name='error'):

        payload = {}
        if exc_type:
            payload['exc_type'] = exc_type
        if exc_val:
            payload['exc_val'] = exc_val

        self.emit_event(
            event_name, payload=payload or None, include_status=True
        )
        self.action_stack.pop(self)

    def emit_event(self, suffix, payload=None, event_class=None, level=None,
                   raw_msg='', raw_args=None, raw_kwargs=None,
                   include_params=False, include_status=False):

        if level is None:
            level = self.level

        # Get `event`, `status` and `guid/id` fields
        event_params = self._event_context(
            suffix, level,
            include_params=include_params, include_status=include_status,
        )

        # Update with user-given fields allowing him to override what he wants
        if payload:
            event_params.update(payload)

        if raw_msg:
            event_params['raw'] = raw_msg

        event = (event_class or Event)(event_params)

        serializer = KeyValueSerializer(event, inline=['raw'])
        format_string = serializer.format_string()
        arguments = serializer.arguments()

        args = chain(arguments, raw_args or ())

        logger = self.get_logger()
        logger.log(level, format_string, *args, **(raw_kwargs or {}))

    def add_params(self, **params):
        self.params.update(params)

    def add_args(self, *args):
        self.params.setdefault('args', []).extend(args)

    def add_kwargs(self, **kwargs):
        self.params.setdefault('kwargs', {}).update(kwargs)

    # Coz why not?
    add_param = add_params
    add_arg = add_args
    add_kwarg = add_kwargs

    def add_result(self, result):
        self.params['result'] = result

    def set_status(self, code, message):
        self.status_code = code
        self.status_message = message

    def _get_name(self):
        return self.name

    def _event_context(self, suffix, level, include_params=False,
                      include_status=False):
        context = {
            'ts': create_ts(),
            'event': '%s.%s' % (self._get_name(), suffix),
            'level': level,
        }

        context.update(self._get_root_uid_item())

        filtered_params = self._filter_hidden_params(self.params)
        cleansed_params = self._cleanse_params(filtered_params)

        if include_params:
            context.update(cleansed_params)

        if include_status:
            context.update(status_code=self.status_code)
            if self.status_message:
                context.update(status_msg=self.status_message)
            if 'result' in cleansed_params:
                context.update(result=cleansed_params['result'])

        return context

    def get_logger(self):
        logger = self.logger

        if isinstance(self.logger, string_types):
            logger = create_logger(self.logger)

        return logger

    def get_uid_item(self):
        if self.uid is None:
            self.uid_field_name, self.uid = self.generate_uid_tuple()

        return {self.uid_field_name: self.uid}

    def _get_root_uid_item(self):
        return (self.action_stack.root() or self).get_uid_item()

    def _cleanse_params(self, params):
        return {
            k: self.CLEANSED_SUBSTITUTE if k in self.sensitive_params else v
            for k, v in params.items()
        }

    def _filter_hidden_params(self, params):
        return {
            k: v
            for k, v in params.items()
            if k not in self.hide_params
        }
