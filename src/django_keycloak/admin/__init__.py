from django.contrib import admin

from django_keycloak.admin.realm import RealmAdmin
from django_keycloak.admin.server import ServerAdmin
from django_keycloak.models import Server, Realm

admin.site.register(Realm, RealmAdmin)
admin.site.register(Server, ServerAdmin)
