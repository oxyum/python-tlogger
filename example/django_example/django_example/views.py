# -*- mode: python; coding: utf-8; -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.http import HttpResponse

from tlogger import get_logger


logger = get_logger(__name__)


@logger
def home(request):
    logger.debug('just some debug logging...')
    return HttpResponse('Hello I am your HTTP response')
