import mock

from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time
from keycloak.openid_connect import KeycloakOpenidConnect

from django_keycloak.factories import OpenIdConnectProfileFactory
from django_keycloak.tests.mixins import MockTestCaseMixin

import django_keycloak.services.oidc_profile


class ServicesKeycloakOpenIDProfileGetActiveAccessTokenTestCase(
        MockTestCaseMixin, TestCase):

    def setUp(self):
        self.oidc_profile = OpenIdConnectProfileFactory(
            access_token='access-token',
            expires_before=datetime(2018, 3, 5, 1, 0, 0),
            refresh_token='refresh-token',
            refresh_expires_before=datetime(2018, 3, 5, 2, 0, 0)
        )
        self.oidc_profile.realm.client.openid_api_client = mock.MagicMock(
            spec_set=KeycloakOpenidConnect)
        self.oidc_profile.realm.client.openid_api_client.refresh_token\
            .return_value = {
                'access_token': 'new-access-token',
                'expires_in': 600,
                'refresh_token': 'new-refresh-token',
                'refresh_expires_in': 3600
            }

    @freeze_time('2018-03-05 00:59:00')
    def test_not_expired(self):
        """
        Case: access token get fetched and is not yet expired
        Expected: current token is returned
        """
        access_token = django_keycloak.services.oidc_profile\
            .get_active_access_token(oidc_profile=self.oidc_profile)

        self.assertEqual(access_token, 'access-token')
        self.assertFalse(
            self.oidc_profile.realm.client.openid_api_client.refresh_token
                .called
        )

    @freeze_time('2018-03-05 01:01:00')
    def test_expired(self):
        """
        Case: access token get requested but current one is expired
        Expected: A new one get requested
        """
        access_token = django_keycloak.services.oidc_profile \
            .get_active_access_token(oidc_profile=self.oidc_profile)

        self.assertEqual(access_token, 'new-access-token')
        self.oidc_profile.realm.client.openid_api_client.refresh_token\
            .assert_called_once_with(refresh_token='refresh-token')

        self.oidc_profile.refresh_from_db()
        self.assertEqual(self.oidc_profile.access_token, 'new-access-token')
        self.assertEqual(self.oidc_profile.expires_before,
                         datetime(2018, 3, 5, 1, 11, 0))
        self.assertEqual(self.oidc_profile.refresh_token, 'new-refresh-token')
        self.assertEqual(self.oidc_profile.refresh_expires_before,
                         datetime(2018, 3, 5, 2, 1, 0))
