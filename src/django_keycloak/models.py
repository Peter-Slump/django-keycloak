import json
import logging
import uuid

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property

logger = logging.getLogger(__name__)


class TokenStorage(models.Model):
    access_token = models.TextField(null=True)
    expires_before = models.DateTimeField(null=True)

    refresh_token = models.TextField(null=True)
    refresh_expires_before = models.DateTimeField(null=True)

    class Meta(object):
        abstract = True


class KeycloakOpenIDProfile(TokenStorage):

    sub = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='oidc_profile',
                                on_delete=models.CASCADE)

    realm = models.ForeignKey('django_keycloak.Realm',
                              related_name='openid_profiles',
                              on_delete=models.CASCADE)


class Nonce(models.Model):

    state = models.UUIDField(default=uuid.uuid4, unique=True)
    redirect_uri = models.CharField(max_length=255)
    next_path = models.CharField(max_length=255, null=True)


class Realm(TokenStorage):

    server_url = models.CharField(max_length=255)

    internal_server_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='URL on internal netwerk calls. For example when used with '
                  'Docker Compose. Only supply when internal calls should go '
                  'to a different url as the end-user will communicate with.'
    )

    name = models.CharField(max_length=255, unique=True,
                            help_text='Name as known on the Keycloak server. '
                                      'This name is used in the API paths '
                                      'of this Realm.')

    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    _certs = models.TextField()

    @property
    def certs(self):
        return json.loads(self._certs)

    @certs.setter
    def certs(self, content):
        self._certs = json.dumps(content)

    _well_known_oidc = models.TextField(blank=True)

    @property
    def well_known_oidc(self):
        return json.loads(self._well_known_oidc)

    @well_known_oidc.setter
    def well_known_oidc(self, content):
        self._well_known_oidc = json.dumps(content)

    _well_known_uma = models.TextField(blank=True)

    @property
    def well_known_uma(self):
        return json.loads(self._well_known_uma)

    @well_known_uma.setter
    def well_known_uma(self, content):
        self._well_known_uma = json.dumps(content)

    _keycloak_realm = None

    @cached_property
    def keycloak_realm(self):
        """
        :rtype: keycloak.realm.Realm
        """
        if self._keycloak_realm is None:
            import django_keycloak.services.realm
            self._keycloak_realm = django_keycloak.services.realm.\
                get_keycloak_realm(self)
        return self._keycloak_realm

    @cached_property
    def keycloak_admin(self):
        """
        :rtype: keycloak.admin.KeycloakAdmin
        """
        import django_keycloak.services.realm
        return django_keycloak.services.realm.get_admin_client(realm=self)

    @cached_property
    def keycloak_openid(self):
        """
        :rtype: keycloak.openid_connect.KeycloakOpenidConnect
        """
        import django_keycloak.services.realm
        return django_keycloak.services.realm.get_keycloak_openid(realm=self)

    @cached_property
    def authz(self):
        """
        :rtype: keycloak.authz.KeycloakAuthz
        """
        import django_keycloak.services.realm
        return django_keycloak.services.realm.get_keycloak_authz(realm=self)

    @cached_property
    def uma(self):
        """
        :rtype: keycloak.uma.KeycloakUMA
        """
        import django_keycloak.services.realm
        return django_keycloak.services.realm.get_keycloak_uma(realm=self)

    def __str__(self):
        return self.name


class Role(models.Model):

    realm = models.ForeignKey('django_keycloak.Realm',
                              related_name='roles',
                              on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission,
                                   on_delete=models.CASCADE)

    reference = models.CharField(max_length=50)

    class Meta(object):
        unique_together = (
            ('realm', 'permission')
        )
