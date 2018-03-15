import base64


def credential_representation_from_hash(hash_, temporary=False):
    algorithm, hashIterations, salt, hashedSaltedValue = hash_.split('$')

    return {
        'type': 'password',
        'hashedSaltedValue': hashedSaltedValue,
        'algorithm': algorithm.replace('_', '-'),
        'hashIterations': int(hashIterations),
        'salt': base64.b64encode(salt.encode()).decode('ascii').strip(),
        'temporary': temporary
    }


def add_user(client, user):
    """
    Create user in Keycloak based on a local user including password.

    :param django_keycloak.models.Client client:
    :param django.contrib.auth.models.User user:
    """
    credentials = credential_representation_from_hash(hash_=user.password)

    client.admin_api_client.realms.by_name(client.realm.name).users.create(
        username=user.username,
        credentials=credentials,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        enabled=user.is_active
    )
