from dynamic_fixtures.fixtures import BaseFixture

from django_keycloak.models import Realm, Client


class Fixture(BaseFixture):

    dependencies = (
        ('myapp', '0003_realm'),
    )

    def load(self):
        realm = Realm.objects.get(name='example')

        Client.objects.get_or_create(
            realm=realm,
            client_id='resource-provider',
            secret='f40347aa-728d-4599-aba9-26f4a69d6f1e'
        )


