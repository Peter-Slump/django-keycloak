from django.contrib import admin
from django_keycloak.models import Realm


class RealmAdmin(admin.ModelAdmin):

    readonly_fields = (
        'certs',
        'well_known',
        'access_token',
        'expires_before',
        'refresh_token',
        'refresh_expires_before'
    )


admin.site.register(Realm, RealmAdmin)
