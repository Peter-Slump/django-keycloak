import logging


logger = logging.getLogger(__name__)


def get_keycloak_id(realm):
    """
    Get internal Keycloak id for client configured in Realm
    :param django_keycloak.models.Realm realm:
    :return:
    """
    clients = realm.keycloak_admin.realms.by_name(name=realm.name)\
        .clients.all()
    for client in clients:
        if client['clientId'] == realm.client_id:
            return client['id']

    return None
