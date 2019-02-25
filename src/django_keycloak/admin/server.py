from django.contrib import admin


class ServerAdmin(admin.ModelAdmin):

    fieldsets = (
        ('Location', {
            'fields': ('url', 'internal_url')
        }),
    )
