import json
import logging
import uuid

from django.contrib.auth.models import Permission
from django.db import models
from django.conf import settings
from django.utils.functional import cached_property

logger = logging.getLogger(__name__)


class Server(models.Model):

    url = models.CharField(max_length=255)

    internal_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='URL on internal netwerk calls. For example when used with '
                  'Docker Compose. Only supply when internal calls should go '
                  'to a different url as the end-user will communicate with.'
    )

    def __str__(self):
        return self.url


class Realm(models.Model):

    server = models.ForeignKey(Server, related_name='realms',
                               on_delete=models.CASCADE)

    name = models.CharField(max_length=255, unique=True,
                            help_text='Name as known on the Keycloak server. '
                                      'This name is used in the API paths '
                                      'of this Realm.')
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

    _keycloak_realm = None

    @cached_property
    def realm_api_client(self):
        """
        :rtype: keycloak.realm.Realm
        """
        if self._keycloak_realm is None:
            import django_keycloak.services.realm
            self._keycloak_realm = django_keycloak.services.realm.\
                get_realm_api_client(realm=self)
        return self._keycloak_realm

    def __str__(self):
        return self.name


class Client(models.Model):

    realm = models.OneToOneField(Realm, related_name='client',
                                 on_delete=models.CASCADE)

    client_id = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)

    service_account = models.OneToOneField(settings.AUTH_USER_MODEL,
                                           related_name='keycloak_client',
                                           on_delete=models.CASCADE,
                                           null=True)

    @cached_property
    def admin_api_client(self):
        """
        :rtype: keycloak.admin.KeycloakAdmin
        """
        import django_keycloak.services.client
        return django_keycloak.services.client.get_admin_client(client=self)

    @cached_property
    def openid_api_client(self):
        """
        :rtype: keycloak.openid_connect.KeycloakOpenidConnect
        """
        import django_keycloak.services.client
        return django_keycloak.services.client.get_openid_client(client=self)

    @cached_property
    def authz_api_client(self):
        """
        :rtype: keycloak.authz.KeycloakAuthz
        """
        import django_keycloak.services.client
        return django_keycloak.services.client.get_authz_api_client(
            client=self)

    def __str__(self):
        return self.client_id


class Role(models.Model):

    client = models.ForeignKey('django_keycloak.Client',
                               related_name='roles',
                               on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission,
                                   on_delete=models.CASCADE)
    reference = models.CharField(max_length=50)

    class Meta(object):
        unique_together = (
            ('client', 'permission')
        )


class TokenModelAbstract(models.Model):

    access_token = models.TextField(null=True)
    expires_before = models.DateTimeField(null=True)

    refresh_token = models.TextField(null=True)
    refresh_expires_before = models.DateTimeField(null=True)

    class Meta(object):
        abstract = True


class OpenIdConnectProfile(TokenModelAbstract):

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


class ExchangedToken(TokenModelAbstract):

    oidc_profile = models.ForeignKey('django_keycloak.OpenIdConnectProfile',
                                     on_delete=models.CASCADE)
    remote_client = models.ForeignKey('django_keycloak.RemoteClient',
                                      related_name='exchanged_tokens',
                                      on_delete=models.CASCADE)

    class Meta(object):
        unique_together = (
            ('oidc_profile', 'remote_client'),
        )


class RemoteClient(models.Model):

    name = models.CharField(max_length=255)
    realm = models.ForeignKey('django_keycloak.Realm',
                              related_name='remote_clients',
                              on_delete=models.CASCADE)