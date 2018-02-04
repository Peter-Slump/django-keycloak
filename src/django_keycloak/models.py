import logging
import uuid

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

    # Server URL on internal netwerk calls. For example when used with Docker
    # Compose. Only supply when internal calls should go to a different url as
    # the end-user will communicate with.
    internal_server_url = models.CharField(max_length=255, null=True)

    name = models.CharField(max_length=255, unique=True)

    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)

    certs = models.TextField()

    well_known = models.TextField()

    content_types = models.ManyToManyField(ContentType,
                                           through='django_keycloak.Resource')

    @cached_property
    def keycloak_realm(self):
        """
        :rtype: keycloak.realm.Realm
        """
        import django_keycloak.services.realm
        return django_keycloak.services.realm.get_keycloak_realm(self)

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

    @property
    def certs_obj(self):
        import json
        return json.loads(self.certs)


class Resource(models.Model):

    realm = models.ForeignKey('django_keycloak.Realm',
                              related_name='resources',
                              on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    reference = models.CharField(max_length=50)

    class Meta(object):
        unique_together = (
            ('realm', 'content_type')
        )
