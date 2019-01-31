from django.contrib.auth import get_user_model

from dynamic_fixtures.fixtures import BaseFixture


class Fixture(BaseFixture):

    def load(self):
        user_model = get_user_model()

        if not user_model.objects.filter(username='admin').exists():
            user_model.objects.create_superuser(username='admin',
                                                password='password',
                                                email='admin@example.com')
