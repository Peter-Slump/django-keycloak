import logging

from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from django_keycloak.models import Realm


logger = logging.getLogger(__name__)


def get_realm(request):
    if not hasattr(request, '_cached_realm'):
        request._cached_realm = Realm.objects.first()
    return request._cached_realm


class BaseKeycloakMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        Adds Realm to request.
        :param request: django request
        """
        request.realm = SimpleLazyObject(lambda: get_realm(request))
