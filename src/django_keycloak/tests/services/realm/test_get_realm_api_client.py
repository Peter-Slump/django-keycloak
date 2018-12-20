from django.test import TestCase

from django_keycloak.factories import ServerFactory, RealmFactory
from django_keycloak.tests.mixins import MockTestCaseMixin

import django_keycloak.services.realm


class ServicesRealmGetRealmApiClientTestCase(
        MockTestCaseMixin, TestCase):

    def setUp(self):
        self.server = ServerFactory(
            url='https://some-url',
            internal_url=''
        )

        self.realm = RealmFactory(
            server=self.server,
            name='test-realm'
        )

    def test_get_realm_api_client(self):
        """
        Case: a realm api client is requested for a realm on a server without
        internal_url.
        Expected: a KeycloakRealm client is returned with settings based on the
        provided realm. The server_url in the client is the provided url.
        """
        client = django_keycloak.services.realm.\
            get_realm_api_client(realm=self.realm)

        self.assertEqual(client.server_url, self.server.url)
        self.assertEqual(client.realm_name, self.realm.name)

    def test_get_realm_api_client_with_internal_url(self):
        """
        Case: a realm api client is requested for a realm on a server with
        internal_url.
        Expected: a KeycloakRealm client is returned with settings based on the
        provided realm. The server_url in the client is the provided url.
        """
        self.server.internal_url = 'https://some-internal-url'

        client = django_keycloak.services.realm.\
            get_realm_api_client(realm=self.realm)

        self.assertEqual(client.server_url, self.server.internal_url)
        self.assertEqual(client.realm_name, self.realm.name)
