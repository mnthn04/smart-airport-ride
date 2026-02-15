from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'created_at', 'updated_at')
    search_fields = ('name', 'phone')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
