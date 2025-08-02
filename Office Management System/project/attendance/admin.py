from django.contrib import admin
from .models import Attendance, LeaveRequest, PublicHoliday
from django.utils import timezone
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'clock_in', 'clock_out', 'working_hours')
    list_filter = ('date', 'user__username')
    search_fields = ('user__username',)
    readonly_fields = ('working_hours',) # working_hours is calculated automatically

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'status', 'requested_at', 'approved_by')
    list_filter = ('status', 'start_date', 'end_date', 'user__username')
    search_fields = ('user__username', 'reason')
    actions = ['approve_leave_requests', 'reject_leave_requests']

    # Custom admin actions for approving/rejecting leave requests
    def approve_leave_requests(self, request, queryset):
        # Only allow Admin or Manager to approve/reject
        if request.user.role in ['Admin', 'Manager']:
            updated_count = queryset.filter(status='Pending').update(
                status='Approved',
                approved_by=request.user,
                approval_date=timezone.now()
            )
            self.message_user(request, f"{updated_count} leave requests approved.")
        else:
            self.message_user(request, "You do not have permission to approve leave requests.", level='error')
    approve_leave_requests.short_description = "Approve selected leave requests"

    def reject_leave_requests(self, request, queryset):
        if request.user.role in ['Admin', 'Manager']:
            updated_count = queryset.filter(status='Pending').update(
                status='Rejected',
                approved_by=request.user,
                approval_date=timezone.now()
            )
            self.message_user(request, f"{updated_count} leave requests rejected.")
        else:
            self.message_user(request, "You do not have permission to reject leave requests.", level='error')
    reject_leave_requests.short_description = "Reject selected leave requests"

    # Override get_queryset to show all requests to Admin/Manager, only own to Employee
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.role in ['Admin', 'Manager']:
            return qs
        return qs.filter(user=request.user)

    # Override formfield_for_foreignkey to limit approved_by choices to Managers/Admins
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "approved_by":
            from employees.models import User # Import User model from employees app
            kwargs["queryset"] = User.objects.filter(role__in=['Admin', 'Manager'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'name')
    search_fields = ('name',)
    list_filter = ('date',)

