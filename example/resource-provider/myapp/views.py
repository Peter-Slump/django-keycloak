# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import requests

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from django.views.generic.base import TemplateView
from jose.exceptions import JWTError

import django_keycloak.services.oidc_profile
import django_keycloak.services.remote_client


logger = logging.getLogger(__name__)


class Home(TemplateView):
    template_name = 'myapp/home.html'


class Secured(LoginRequiredMixin, TemplateView):
    template_name = 'myapp/secured.html'

    def call_api(self):
        if not hasattr(self.request.user, 'oidc_profile'):
            return None
        oidc_profile = self.request.user.oidc_profile
        remote_client = oidc_profile.realm.remote_clients.get(
            name='resource-provider-api')

        access_token = django_keycloak.services.remote_client.get_active_remote_client_token(
            oidc_profile=oidc_profile, remote_client=remote_client)

        result = requests.get(
            'https://resource-provider-api.localhost.yarf.nl/api/authenticated-end-point',
            verify=False,
            headers={
                'Authorization': 'Bearer {}'.format(access_token)
            }
        )
        return result.json()

    def get_context_data(self, **kwargs):
        api_result = self.call_api()
        try:
            jwt = self.get_decoded_jwt()
        except JWTError:
            jwt = None

        return super(Secured, self).get_context_data(
            permissions=self.request.user.get_all_permissions(),
            api_result=api_result,
            jwt=json.dumps(jwt, sort_keys=True, indent=4, separators=(',', ': ')) if jwt else None,
            op_location=self.request.realm.well_known_oidc['check_session_iframe'],
            **kwargs
        )

    def get_decoded_jwt(self):
        if not hasattr(self.request.user, 'oidc_profile'):
            return None

        oidc_profile = self.request.user.oidc_profile
        client = oidc_profile.realm.client

        return client.openid_api_client.decode_token(
            token=oidc_profile.access_token,
            key=client.realm.certs,
            algorithms=client.openid_api_client.well_known[
                'id_token_signing_alg_values_supported']
        )


class Permission(PermissionRequiredMixin, TemplateView):
    raise_exception = True
    template_name = 'myapp/permission.html'
    permission_required = 'some-permission'
