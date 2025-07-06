from django.contrib import admin
from .models import Client, Town


@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('eik', 'name', 'town', 'is_active')
    list_filter = ('is_active', 'town')
    search_fields = ('eik', 'name')
