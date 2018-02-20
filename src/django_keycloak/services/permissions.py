import logging

from django.contrib.auth.models import Permission
from requests.exceptions import HTTPError

import django_keycloak.services.client

logger = logging.getLogger(__name__)


def synchronize(realm):
    """
    :param django_keycloak.models.Realm realm:
    :return:
    """
    keycloak_client_id = django_keycloak.services.client.get_keycloak_id(
        realm=realm)

    for permission in Permission.objects.all():

        try:
            realm.keycloak_admin.realms.by_name(realm.name)\
                .clients.by_id(keycloak_client_id)\
                .roles.create(name=permission.codename,
                              description=permission.name)
        except HTTPError as e:
            if e.response.status_code != 409:
                raise

        else:
            continue

        # Update role
        realm.keycloak_admin.realms.by_name(realm.name) \
            .clients.by_id(keycloak_client_id) \
            .roles.by_name(permission.codename) \
            .update(name=permission.codename, description=permission.name)
