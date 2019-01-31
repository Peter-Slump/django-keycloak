from django.test import TestCase

from django_keycloak.factories import OpenIdConnectProfileFactory
from django_keycloak.tests.mixins import MockTestCaseMixin
from django_keycloak.auth.backends import KeycloakAuthorizationBase


class BackendsKeycloakAuthorizationBaseHasPermTestCase(
        MockTestCaseMixin, TestCase):

    def setUp(self):
        self.backend = KeycloakAuthorizationBase()

        self.profile = OpenIdConnectProfileFactory()

        self.setup_mock(
            'django_keycloak.auth.backends.KeycloakAuthorizationBase.'
            'get_all_permissions',
            return_value=[
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
        )

    def test_resource_scope_should_have_permission(self):
        """
        Case: Permission is expected that is available to the user.
        Expected: Permission granted.
        """
        permission = self.backend.has_perm(
            user_obj=self.profile.user, perm='Resource.Read')

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
            user_obj=self.profile.user, perm='Resource.Create')

        self.assertFalse(permission)

    def test_other_resource_other_scope_should_not_have_permission(self):
        """"
        Case: Permission is expected that is not available to the user
        according to the RPT.
        Expected: Permission denied.
        """
        permission = self.backend.has_perm(
            user_obj=self.profile.user, perm='OtherResource.OtherScope')

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
