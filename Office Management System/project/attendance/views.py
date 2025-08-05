from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, fields
from datetime import timedelta
from .models import Attendance, LeaveRequest, PublicHoliday
from .forms import AttendanceForm, LeaveRequestForm, LeaveApprovalForm
from employees.models import User # Import User model for role checks

# Helper functions (copied from employees app for convenience, or you could put them in a common utility file)
def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

def is_manager_or_admin(user):
    return user.is_authenticated and (user.role == 'Manager' or user.role == 'Admin')

def is_employee(user):
    return user.is_authenticated and user.role == 'Employee'

# --- Attendance Views ---

@login_required
@user_passes_test(is_employee) # Only employees can clock in/out
def clock_in_out(request):
    today = timezone.localdate()
    # Try to get today's attendance record for the current user
    attendance, created = Attendance.objects.get_or_create(user=request.user, date=today)

    if request.method == 'POST':
        if 'clock_in' in request.POST:
            if not attendance.clock_in:
                attendance.clock_in = timezone.now()
                attendance.save()
                # Redirect to prevent resubmission on refresh
                return redirect('clock_in_out')
            else:
                # You might want to add a message here that user is already clocked in
                pass
        elif 'clock_out' in request.POST:
            if attendance.clock_in and not attendance.clock_out:
                attendance.clock_out = timezone.now()
                attendance.save()
                # Redirect to prevent resubmission on refresh
                return redirect('clock_in_out')
            elif not attendance.clock_in:
                # User tried to clock out without clocking in
                pass
            else:
                # User already clocked out
                pass

    context = {
        'attendance': attendance,
        'today': today,
        'message': 'You are currently clocked in.' if attendance.clock_in and not attendance.clock_out else ''
    }
    return render(request, 'attendance/clock_in_out.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_manager_or_admin(u) or is_employee(u))
def attendance_history(request):
    if is_admin(request.user) or is_manager_or_admin(request.user):
        # Admin/Manager sees all attendance records
        attendances = Attendance.objects.select_related('user').all().order_by('-date', 'user__username')
    else:
        # Employee sees only their own attendance records
        attendances = Attendance.objects.filter(user=request.user).order_by('-date')

    context = {
        'attendances': attendances,
        'is_manager_or_admin': is_manager_or_admin(request.user) # For template logic
    }
    return render(request, 'attendance/attendance_history.html', context)


# --- Leave Views ---

@login_required
@user_passes_test(is_employee) # Only employees can request leave
def request_leave(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            return redirect('leave_list') # Redirect to view all leave requests
    else:
        form = LeaveRequestForm()
    context = {'form': form, 'form_title': 'Request New Leave'}
    return render(request, 'attendance/leave_request_form.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_manager_or_admin(u) or is_employee(u))
def leave_list(request):
    if is_admin(request.user) or is_manager_or_admin(request.user):
        # Admin/Manager sees all leave requests
        leave_requests = LeaveRequest.objects.select_related('user').all().order_by('-requested_at')
    else:
        # Employee sees only their own leave requests
        leave_requests = LeaveRequest.objects.filter(user=request.user).order_by('-requested_at')

    context = {
        'leave_requests': leave_requests,
        'is_manager_or_admin': is_manager_or_admin(request.user) # For template logic
    }
    return render(request, 'attendance/leave_list.html', context)

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can approve/reject
def approve_reject_leave(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST, instance=leave_request)
        if form.is_valid():
            leave_request.approved_by = request.user
            leave_request.approval_date = timezone.now()
            form.save()
            return redirect('leave_list')
    else:
        form = LeaveApprovalForm(instance=leave_request)

    context = {
        'leave_request': leave_request,
        'form': form,
        'form_title': f"Review Leave Request by {leave_request.user.username}"
    }
    return render(request, 'attendance/leave_detail.html', context)

# --- Public Holiday Views ---

@login_required
def public_holidays_list(request):
    holidays = PublicHoliday.objects.all().order_by('date')
    context = {'holidays': holidays}
    return render(request, 'attendance/public_holidays_list.html', context)
