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

import django_keycloak.services.oidc_profile


logger = logging.getLogger(__name__)


class Login(RedirectView):

    def get_redirect_url(self, *args, **kwargs):

        nonce = Nonce.objects.create(
            redirect_uri=self.request.build_absolute_uri(
                location=reverse('login-complete')),
            next_path=self.request.GET.get('next'))

        self.request.session['oidc_state'] = str(nonce.state)

        authorization_url = self.request.realm.client.openid_api_client\
            .authorization_url(
                redirect_uri=nonce.redirect_uri,
                scope='openid given_name family_name email uma_authorization',
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
        if 'error' in self.request.GET:
            return HttpResponseServerError(self.request.GET['error'])

        if 'code' not in self.request.GET and 'state' not in self.request.GET:
            return HttpResponseBadRequest()

        if self.request.GET['state'] != self.request.session['oidc_state']:
            return HttpResponseBadRequest()

        nonce = Nonce.objects.get(state=self.request.GET['state'])

        user = authenticate(request=self.request,
                            code=self.request.GET['code'],
                            redirect_uri=nonce.redirect_uri)
        login(self.request, user)

        nonce.delete()
        return HttpResponseRedirect(nonce.next_path or '/')


class Logout(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if hasattr(self.request.user, 'oidc_profile'):
            self.request.realm.client.openid_api_client.logout(
                self.request.user.oidc_profile.refresh_token
            )
        logout(self.request)

        if settings.LOGOUT_REDIRECT_URL:
            return resolve_url(settings.LOGOUT_REDIRECT_URL)

        return reverse('keycloak_login')


class SessionIframe(TemplateView):
    template_name = 'django_keycloak/session_iframe.html'

    def get_decoded_jwt(self):
        if not hasattr(self.request.user, 'oidc_profile'):
            return None

        oidc_profile = self.request.user.oidc_profile
        client = oidc_profile.realm.client

        active_access_token = django_keycloak.services.oidc_profile\
            .get_active_access_token(oidc_profile=oidc_profile)

        return client.openid_api_client.decode_token(
            token=active_access_token,
            key=client.realm.certs,
            algorithms=client.openid_api_client.well_known[
                'id_token_signing_alg_values_supported']
        )

    @property
    def client_id(self):
        if not hasattr(self.request, 'realm'):
            return None

        realm = self.request.realm
        return realm.client.client_id

    def get_context_data(self, **kwargs):
        jwt = self.get_decoded_jwt()
        return super(SessionIframe, self).get_context_data(
            client_id=self.client_id,
            session_state=jwt['session_state'],
            identity_server=self.request.realm.server.url
        )
