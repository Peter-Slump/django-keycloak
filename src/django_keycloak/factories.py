import factory

from django.contrib.auth import get_user_model

from django_keycloak.models import Realm, KeycloakOpenIDProfile


class UserFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = get_user_model()

    username = factory.Faker('user_name')


class RealmFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = Realm

    server_url = factory.Faker('url', schemes=['https'])

    name = factory.Faker('slug')

    client_id = factory.Faker('slug')
    client_secret = factory.Faker('uuid4')

    _well_known_oidc = ''


class KeycloakOpenIDProfileFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = KeycloakOpenIDProfile

    sub = factory.Faker('uuid4')
    realm = factory.SubFactory(RealmFactory)
    user = factory.SubFactory(UserFactory)
