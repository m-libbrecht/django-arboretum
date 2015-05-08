from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from demoapp.models import Domain


class DomainAdmin(MPTTModelAdmin):
    pass
admin.site.register(Domain, DomainAdmin)
