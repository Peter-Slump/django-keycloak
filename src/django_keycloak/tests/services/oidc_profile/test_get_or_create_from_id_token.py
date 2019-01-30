import mock

from datetime import datetime

from django.test import TestCase
from keycloak.openid_connect import KeycloakOpenidConnect

from django_keycloak.factories import ClientFactory, \
    OpenIdConnectProfileFactory, UserFactory
from django_keycloak.tests.mixins import MockTestCaseMixin

import django_keycloak.services.oidc_profile


class ServicesOpenIDProfileGetOrCreateFromIdTokenTestCase(
        MockTestCaseMixin, TestCase):

    def setUp(self):
        self.client = ClientFactory(
            realm___certs='{}',
            realm___well_known_oidc='{"issuer": "https://issuer"}'
        )
        self.client.openid_api_client = mock.MagicMock(
            spec_set=KeycloakOpenidConnect)
        self.client.openid_api_client.well_known = {
            'id_token_signing_alg_values_supported': ['signing-alg']
        }
        self.client.openid_api_client.decode_token.return_value = {
            'sub': 'some-sub',
            'email': 'test@example.com',
            'given_name': 'Some given name',
            'family_name': 'Some family name'
        }

    def test_create_with_new_user_new_profile(self):
        """
        Case: oidc profile is requested based on a provided id token.
        The user and profile do not exist yet.
        Expected: oidc profile and user are created with information from
        the id token.
        """
        profile = django_keycloak.services.oidc_profile. \
            get_or_create_from_id_token(
                client=self.client, id_token='some-id-token'
            )

        self.client.openid_api_client.decode_token.assert_called_with(
            token='some-id-token',
            key=dict(),
            algorithms=['signing-alg'],
            issuer='https://issuer'
        )

        self.assertEqual(profile.sub, 'some-sub')
        self.assertEqual(profile.user.username, 'some-sub')
        self.assertEqual(profile.user.email, 'test@example.com')
        self.assertEqual(profile.user.first_name, 'Some given name')
        self.assertEqual(profile.user.last_name, 'Some family name')

    def test_update_with_existing_profile_new_user(self):
        """
        Case: oidc profile is requested based on a provided id token.
        The profile exists, but the user doesn't.
        Expected: oidc user is created with information from the id token
        and linked to the profile.
        """
        existing_profile = OpenIdConnectProfileFactory(
            access_token='access-token',
            expires_before=datetime(2018, 3, 5, 1, 0, 0),
            refresh_token='refresh-token',
            sub='some-sub'
        )

        profile = django_keycloak.services.oidc_profile. \
            get_or_create_from_id_token(
                client=self.client, id_token='some-id-token'
            )

        self.client.openid_api_client.decode_token.assert_called_with(
            token='some-id-token',
            key=dict(),
            algorithms=['signing-alg'],
            issuer='https://issuer'
        )

        self.assertEqual(profile.sub, 'some-sub')
        self.assertEqual(profile.pk, existing_profile.pk)
        self.assertEqual(profile.user.username, 'some-sub')
        self.assertEqual(profile.user.email, 'test@example.com')
        self.assertEqual(profile.user.first_name, 'Some given name')
        self.assertEqual(profile.user.last_name, 'Some family name')

    def test_create_with_existing_user_new_profile(self):
        """
        Case: oidc profile is requested based on a provided id token.
        The user exists, but the profile doesn't.
        Expected: oidc profile is created and user is linked to the profile.
        """
        existing_user = UserFactory(
            username='some-sub'
        )

        profile = django_keycloak.services.oidc_profile.\
            get_or_create_from_id_token(
                client=self.client, id_token='some-id-token'
            )

        self.client.openid_api_client.decode_token.assert_called_with(
            token='some-id-token',
            key=dict(),
            algorithms=['signing-alg'],
            issuer='https://issuer'
        )

        self.assertEqual(profile.sub, 'some-sub')
        self.assertEqual(profile.user.pk, existing_user.pk)
        self.assertEqual(profile.user.username, 'some-sub')
        self.assertEqual(profile.user.email, 'test@example.com')
        self.assertEqual(profile.user.first_name, 'Some given name')
        self.assertEqual(profile.user.last_name, 'Some family name')

    def test_create_with_existing_user_existing_profile(self):
        """
        Case: oidc profile is requested based on a provided id token.
        The user and profile already exist.
        Expected: existing oidc profile is returned with existing user linked
        to it.
        """
        existing_user = UserFactory(
            username='some-sub'
        )

        existing_profile = OpenIdConnectProfileFactory(
            access_token='access-token',
            expires_before=datetime(2018, 3, 5, 1, 0, 0),
            refresh_token='refresh-token',
            sub='some-sub'
        )

        profile = django_keycloak.services.oidc_profile.\
            get_or_create_from_id_token(
                client=self.client, id_token='some-id-token'
            )

        self.client.openid_api_client.decode_token.assert_called_with(
            token='some-id-token',
            key=dict(),
            algorithms=['signing-alg'],
            issuer='https://issuer'
        )

        self.assertEqual(profile.pk, existing_profile.pk)
        self.assertEqual(profile.sub, 'some-sub')
        self.assertEqual(profile.user.pk, existing_user.pk)
        self.assertEqual(profile.user.username, 'some-sub')
        self.assertEqual(profile.user.email, 'test@example.com')
        self.assertEqual(profile.user.first_name, 'Some given name')
        self.assertEqual(profile.user.last_name, 'Some family name')
