from django.test import TestCase, override_settings

from django_keycloak.factories import OpenIdConnectProfileFactory
from django_keycloak.tests.mixins import MockTestCaseMixin
from django_keycloak.auth.backends import KeycloakAuthorizationBase


@override_settings(KEYCLOAK_PERMISSIONS_METHOD='resource')
class BackendsKeycloakAuthorizationBaseHasPermTestCase(
        MockTestCaseMixin, TestCase):

    def setUp(self):
        self.backend = KeycloakAuthorizationBase()

        self.profile = OpenIdConnectProfileFactory(user__is_active=True)

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
            }
        )

    def test_resource_scope_should_have_permission(self):
        """
        Case: Permission is expected that is available to the user.
        Expected: Permission granted.
        """
        permission = self.backend.has_perm(
            user_obj=self.profile.user, perm='Read_Resource')

        self.assertTrue(permission)

    def test_resource_no_scope_should_not_have_permission(self):
        """"
        Case: Permission is formatted as resource only which does not exist as
        such in the RPT.
        Expected: Permission denied.
        """
        permission = self.backend.has_perm(
            user_obj=self.profile.user, perm='Resource')

        self.assertFalse(permission)

    def test_resource_other_scope_should_not_have_permission(self):
        """"
        Case: Permission is expected with a scope that is not available to
        the user according to the RPT.
        Expected: Permission denied.
        """
        permission = self.backend.has_perm(
            user_obj=self.profile.user, perm='Create_Resource')

        self.assertFalse(permission)

    def test_other_resource_other_scope_should_not_have_permission(self):
        """"
        Case: Permission is expected that is not available to the user
        according to the RPT.
        Expected: Permission denied.
        """
        permission = self.backend.has_perm(
            user_obj=self.profile.user, perm='OtherScope_OtherResource')

        self.assertFalse(permission)

    def test_resource_no_scope_should_have_permission(self):
        """"
        Case: Permission is expected with no scope provided, but scope is
        also not provided in the RPT.
        Expected: Permission granted.
        """
        permission = self.backend.has_perm(
            user_obj=self.profile.user, perm='Resource2')

        self.assertTrue(permission)
