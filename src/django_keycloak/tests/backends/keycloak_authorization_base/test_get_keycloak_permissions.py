from django.test import TestCase, override_settings

from django_keycloak.factories import OpenIdConnectProfileFactory
from django_keycloak.tests.mixins import MockTestCaseMixin
from django_keycloak.auth.backends import KeycloakAuthorizationBase


@override_settings(KEYCLOAK_PERMISSIONS_METHOD='resource')
class BackendsKeycloakAuthorizationBaseGetKeycloakPermissionsTestCase(
        MockTestCaseMixin, TestCase):

    def setUp(self):
        self.backend = KeycloakAuthorizationBase()

        self.profile = OpenIdConnectProfileFactory()

        self.setup_mock(
            'django_keycloak.services.oidc_profile.get_entitlement',
            return_value={
                'authorization': {
                    'permissions': [
                        {
                            'resource_set_name': 'Resource',
                            'scopes': [
                                'Read',
                                'Update'
                            ]
                        },
                        {
                            'resource_set_name': 'Resource2'
                        }
                    ]
                }
            })

    def test_get_keycloak_permissions(self):
        """
        Case: The permissions are requested from Keycloak, which are returned
        by get_entitlement as a decoded RPT.
        Expect: The permissions are extracted from the RPT and are returned
        in a list.
        """
        permissions = self.backend.get_keycloak_permissions(
            user_obj=self.profile.user)

        self.assertListEqual(
            ['Read_Resource', 'Update_Resource', 'Resource2'],
            permissions
        )
