# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.http.response import JsonResponse

logger = logging.getLogger(__name__)


def api_end_point(request):
    return JsonResponse({'foo': 'bar'})


def authenticated_end_point(request):

    return JsonResponse({
        'user': {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        }
    })