from dynamic_fixtures.fixtures import BaseFixture

from django_keycloak.models import Server


class Fixture(BaseFixture):

    def load(self):
        Server.objects.get_or_create(
            url='https://identity.localhost.yarf.nl'
        )
