import factory

from django.contrib.auth import get_user_model

from django_keycloak.models import (
    Client,
    OpenIdConnectProfile,
    Realm,
    Server
)


class UserFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = get_user_model()

    username = factory.Faker('user_name')


class ServerFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = Server

    url = factory.Faker('url', schemes=['https'])


class RealmFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = Realm

    server = factory.SubFactory(ServerFactory)

    name = factory.Faker('slug')

    _certs = ''
    _well_known_oidc = '{}'

    client = factory.RelatedFactory('django_keycloak.factories.ClientFactory',
                                    'realm')


class OpenIdConnectProfileFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = OpenIdConnectProfile

    sub = factory.Faker('uuid4')
    realm = factory.SubFactory(RealmFactory)
    user = factory.SubFactory(UserFactory)


class ClientFactory(factory.DjangoModelFactory):

    class Meta(object):
        model = Client

    realm = factory.SubFactory(RealmFactory, client=None)
    service_account_profile = factory.SubFactory(
        OpenIdConnectProfileFactory,
        realm=factory.SelfAttribute('..realm')
    )

    client_id = factory.Faker('slug')
    secret = factory.Faker('uuid4')
