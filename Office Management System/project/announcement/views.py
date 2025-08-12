from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q # For complex queries
from .models import Announcement
from .forms import AnnouncementForm
from employees.models import User # Import User model for role checks

# Helper functions (copied from employees app for convenience, or you could put them in a common utility file)
def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

def is_manager_or_admin(user):
    return user.is_authenticated and (user.role == 'Manager' or user.role == 'Admin')

def is_employee(user):
    return user.is_authenticated and user.role == 'Employee'

# --- Announcement Views ---

@login_required
def announcement_list(request):
    # Filter announcements based on user's role
    if is_admin(request.user):
        announcements = Announcement.objects.all().order_by('-created_at')
    elif is_manager_or_admin(request.user):
        announcements = Announcement.objects.filter(
            Q(visible_to='all') | Q(visible_to='manager')
        ).order_by('-created_at')
    else: # Employee
        announcements = Announcement.objects.filter(
            Q(visible_to='all') | Q(visible_to='employee')
        ).order_by('-created_at')

    context = {
        'announcements': announcements,
        'can_manage_announcements': is_manager_or_admin(request.user) # Only managers/admins can add/edit/delete
    }
    return render(request, 'announcements/announcement_list.html', context)

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can add announcements
def announcement_add(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    context = {'form': form, 'form_title': 'Create New Announcement'}
    return render(request, 'announcements/announcement_form.html', context)

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can edit announcements
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    # Further permission check: Only the creator or an Admin can edit
    if not (announcement.created_by == request.user or is_admin(request.user)):
        return redirect('announcement_list') # Or render a permission denied page

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            return redirect('announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    context = {'form': form, 'form_title': f'Edit Announcement: {announcement.title}'}
    return render(request, 'announcements/announcement_form.html', context)

@login_required
@user_passes_test(is_admin) # Only Admin can delete announcements
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        return redirect('announcement_list')
    context = {'announcement': announcement}
    return render(request, 'announcements/announcement_confirm_delete.html', context)
