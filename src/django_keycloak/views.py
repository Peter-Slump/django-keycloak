# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.shortcuts import resolve_url

try:
    from urllib.parse import urljoin  # noqa: F401
except ImportError:
    from urlparse import urljoin  # noqa: F401

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http.response import (
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseRedirect
)
from django.urls.base import reverse
from django.views.generic.base import (
    RedirectView,
    TemplateView
)

from django_keycloak.models import Nonce
from django_keycloak.auth import remote_user_login


logger = logging.getLogger(__name__)


class Login(RedirectView):

    def get_redirect_url(self, *args, **kwargs):

        nonce = Nonce.objects.create(
            redirect_uri=self.request.build_absolute_uri(
                location=reverse('keycloak_login_complete')),
            next_path=self.request.GET.get('next'))

        self.request.session['oidc_state'] = str(nonce.state)

        authorization_url = self.request.realm.client.openid_api_client\
            .authorization_url(
                redirect_uri=nonce.redirect_uri,
                scope='openid given_name family_name email',
                state=str(nonce.state)
            )

        if self.request.realm.server.internal_url:
            authorization_url = authorization_url.replace(
                self.request.realm.server.internal_url,
                self.request.realm.server.url,
                1
            )

        logger.debug(authorization_url)

        return authorization_url


class LoginComplete(RedirectView):

    def get(self, *args, **kwargs):
        request = self.request

        if 'error' in request.GET:
            return HttpResponseServerError(request.GET['error'])

        if 'code' not in request.GET and 'state' not in request.GET:
            return HttpResponseBadRequest()

        if 'oidc_state' not in request.session \
                or request.GET['state'] != request.session['oidc_state']:
            # Missing or incorrect state; login again.
            return HttpResponseRedirect(reverse('keycloak_login'))

        nonce = Nonce.objects.get(state=request.GET['state'])

        user = authenticate(request=request,
                            code=request.GET['code'],
                            redirect_uri=nonce.redirect_uri)

        if getattr(settings, 'AUTH_ENABLE_REMOTE_USER', False):
            remote_user_login(request, user)
        else:
            login(request, user)

        nonce.delete()

        return HttpResponseRedirect(nonce.next_path or '/')


class Logout(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if hasattr(self.request.user, 'oidc_profile'):
            self.request.realm.client.openid_api_client.logout(
                self.request.user.get_profile().refresh_token
            )
        logout(self.request)

        if settings.LOGOUT_REDIRECT_URL:
            return resolve_url(settings.LOGOUT_REDIRECT_URL)

        return reverse('keycloak_login')


class SessionIframe(TemplateView):
    template_name = 'django_keycloak/session_iframe.html'

    @property
    def op_location(self):
        realm = self.request.realm
        return realm.well_known_oidc['check_session_iframe'].replace(
            realm.server.internal_url,
            realm.server.url,
            1
        )

    @property
    def client_id(self):
        if not hasattr(self.request, 'realm'):
            return None

        realm = self.request.realm
        return realm.client.client_id

    def get_context_data(self, **kwargs):
        return super(SessionIframe, self).get_context_data(
            client_id=self.client_id,
            identity_server=self.request.realm.server.url,
            op_location=self.op_location,
            cookie_name=getattr(settings, 'KEYCLOAK_SESSION_STATE_COOKIE_NAME',
                                'session_state')
        )
