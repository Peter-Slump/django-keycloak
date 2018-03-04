import factory

from django_keycloak.models import Realm


class RealmFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = Realm

    server_url = factory.Faker('url', schemes=['https'])

    name = factory.Faker('slug')

    client_id = factory.Faker('slug')
    client_secret = factory.Faker('uuid4')

    _well_known_oidc = ''
