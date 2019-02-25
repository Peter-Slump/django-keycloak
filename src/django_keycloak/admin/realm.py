from django.contrib import admin, messages
from keycloak.exceptions import KeycloakClientError
from requests.exceptions import HTTPError

from django_keycloak.models import (
    Client,
    OpenIdConnectProfile,
    RemoteClient
)
import django_keycloak.services.permissions
import django_keycloak.services.realm
import django_keycloak.services.uma


def refresh_open_id_connect_well_known(modeladmin, request, queryset):
    for realm in queryset:
        django_keycloak.services.realm.refresh_well_known_oidc(realm=realm)
    modeladmin.message_user(
        request=request,
        message='OpenID Connect .well-known refreshed',
        level=messages.SUCCESS
    )


refresh_open_id_connect_well_known.short_description = 'Refresh OpenID ' \
                                                       'Connect .well-known'


def refresh_certs(modeladmin, request, queryset):
    for realm in queryset:
        django_keycloak.services.realm.refresh_certs(realm=realm)
    modeladmin.message_user(
        request=request,
        message='Certificates refreshed',
        level=messages.SUCCESS
    )


refresh_certs.short_description = 'Refresh Certificates'


def clear_client_tokens(modeladmin, request, queryset):
    OpenIdConnectProfile.objects.filter(realm__in=queryset).update(
        access_token=None,
        expires_before=None,
        refresh_token=None,
        refresh_expires_before=None
    )
    modeladmin.message_user(
        request=request,
        message='Tokens cleared',
        level=messages.SUCCESS
    )


clear_client_tokens.short_description = 'Clear client tokens'


def synchronize_permissions(modeladmin, request, queryset):
    for realm in queryset:
        try:
            django_keycloak.services.permissions.synchronize(
                client=realm.client)
        except HTTPError as e:
            if e.response.status_code == 403:
                modeladmin.message_user(
                    request=request,
                    message='Forbidden for {}. Does the client\'s service '
                            'account has the "keycloak_client" role?'.format(
                                realm.name
                            ),
                    level=messages.ERROR
                )
                return
            else:
                raise
    modeladmin.message_user(
        request=request,
        message='Permissions synchronized',
        level=messages.SUCCESS
    )


synchronize_permissions.short_description = 'Synchronize permissions'


def synchronize_resources(modeladmin, request, queryset):
    for realm in queryset:
        try:
            django_keycloak.services.uma.synchronize_client(
                client=realm.client)
        except KeycloakClientError as e:
            if e.original_exc.response.status_code == 400:
                modeladmin.message_user(
                    request=request,
                    message='Forbidden for {}. Is "Remote Resource '
                            'Management"  enabled for the related client?'
                            .format(
                                realm.name
                            ),
                    level=messages.ERROR
                )
                return
            else:
                raise
    modeladmin.message_user(
        request=request,
        message='Resources synchronized',
        level=messages.SUCCESS
    )


synchronize_resources.short_description = 'Synchronize models as Keycloak ' \
                                          'resources'


class ClientAdmin(admin.TabularInline):

    model = Client

    fields = ('client_id', 'secret')


class RemoteClientAdmin(admin.TabularInline):

    model = RemoteClient

    extra = 1

    fields = ('name',)


class RealmAdmin(admin.ModelAdmin):

    inlines = [ClientAdmin, RemoteClientAdmin]

    actions = [
        refresh_open_id_connect_well_known,
        refresh_certs,
        clear_client_tokens,
        synchronize_permissions,
        synchronize_resources
    ]

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Location', {
            'fields': ('server', '_well_known_oidc',)
        })

    )

    readonly_fields = ('_well_known_oidc',)
