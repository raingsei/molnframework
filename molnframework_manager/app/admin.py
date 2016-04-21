from django.contrib import admin
from .models import ComputeApp,ComputeService,ComputePod,ComputePodHealth

class ComputePodHealthInline(admin.TabularInline):
    model = ComputePodHealth
    readonly_fields = ('data',)
    extra = 0

    def has_add_permission(self, request):
        return False

class ComputeServiceInline(admin.TabularInline):
    model = ComputeService
    readonly_fields = ('name','url','registered_date','meta_info')
    extra = 0

    def has_add_permission(self, request):
        return False

class ComputePodInline (admin.TabularInline):
    model = ComputePod
    readonly_fields = ('name','address','registered_date','system_info')
    extra = 0

    def has_add_permission(self, request):
        return False

class ComputeAppAdmin(admin.ModelAdmin):
    list_display = ('name','author')
    #readonly_fields = ('name','author','registered_date','number_pods')
    inlines = [ComputePodInline]

class ComputePodAdmin(admin.ModelAdmin):
    list_display = ('name','address','registered_date','compute_app')
    readonly_fields = ('name','address','registered_date')
    inlines = [ComputeServiceInline,ComputePodHealthInline]

admin.site.register(ComputeApp,ComputeAppAdmin)
admin.site.register(ComputePod,ComputePodAdmin)
