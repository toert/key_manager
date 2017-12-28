from django.contrib import admin

from api.models import Key


class KeyAdmin(admin.ModelAdmin):
    readonly_fields = ['last_request_time']


admin.site.register(Key, KeyAdmin)