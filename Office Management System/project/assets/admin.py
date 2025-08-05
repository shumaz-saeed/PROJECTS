from django.contrib import admin
from .models import Asset

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'assigned_to', 'status', 'purchase_date', 'created_at')
    list_filter = ('status', 'assigned_to', 'purchase_date')
    search_fields = ('name', 'serial_number', 'description', 'assigned_to__username')
    raw_id_fields = ('assigned_to',) 
    readonly_fields = ('created_at', 'updated_at')
