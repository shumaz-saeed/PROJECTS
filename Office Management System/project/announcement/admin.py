from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'visible_to')
    list_filter = ('visible_to', 'created_at')
    search_fields = ('title', 'content', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    # Automatically set created_by to the current user when adding from admin
    def save_model(self, request, obj, form, change):
        if not change: # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
