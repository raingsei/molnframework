from django.contrib import admin
from .models import ComputeApp,ComputeService


class ComputeServiceInline(admin.TabularInline):
    model = ComputeService
    extra = 0

    def has_add_permission(self, request):
        return False

class ComputeAppAdmin(admin.ModelAdmin):
    list_display = ('app_name','author')
    inlines = [ComputeServiceInline]

admin.site.register(ComputeApp,ComputeAppAdmin)
