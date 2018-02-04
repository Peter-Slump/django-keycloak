from django.contrib.contenttypes.models import ContentType

from django_keycloak.models import Resource

import django_keycloak.services.realm


def register_as_resource(realm):
    """
    Register a resource for every content type.

    :param django_keycloak.models.Realm realm:
    :return:
    """
    for content_type in ContentType.objects.all():
        access_token = django_keycloak.services.realm.get_access_token(
            realm=realm)

        response = realm.uma.resource_set_create(
            token=access_token,
            name='{}.{}'.format(content_type.app_label, content_type.model),
            type='urn:{}:resources:{}:{}'.format(
                realm.client_id,
                content_type.app_label,
                content_type.model
            ))
        Resource.objects.create(realm=realm, content_type=content_type,
                                reference=response['_id'])
