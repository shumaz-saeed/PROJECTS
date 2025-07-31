from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    list_filter = ('start_date', 'end_date')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'deadline', 'priority')
    list_filter = ('status', 'project', 'assigned_to', 'deadline')
    search_fields = ('title', 'description', 'project__name', 'assigned_to__username')
    raw_id_fields = ('assigned_to',) # Use a raw ID field for assigned_to for better performance with many users

