from django.contrib import admin
from .models import Pool, PoolMember

class PoolMemberInline(admin.TabularInline):
    model = PoolMember
    extra = 1
    autocomplete_fields = ['ride_request']

@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'cab', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('cab__driver_name', 'id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PoolMemberInline]

@admin.register(PoolMember)
class PoolMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'pool', 'ride_request', 'sequence_order', 'pickup_eta')
    list_filter = ('pool', 'sequence_order')
    autocomplete_fields = ['pool', 'ride_request']
