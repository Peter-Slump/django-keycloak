from dynamic_fixtures.fixtures import BaseFixture

from django_keycloak.models import Realm, Server, RemoteClient


class Fixture(BaseFixture):

    dependencies = (
        ('myapp', '0002_server'),
    )

    def load(self):
        server = Server.objects.get(url='https://identity.localhost.yarf.nl')

        realm, created = Realm.objects.get_or_create(
            server=server,
            name='example'
        )

        RemoteClient.objects.get_or_create(
            name='resource-provider-api',
            realm=realm
        )