from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'department', 'access_level')
    list_filter = ('department', 'access_level', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__username', 'department')
    readonly_fields = ('uploaded_at',)

    # Automatically set uploaded_by to the current user when adding from admin
    def save_model(self, request, obj, form, change):
        if not change: # Only on creation
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
