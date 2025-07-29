from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import User, EmployeeProfile
from .forms import CustomUserCreationForm, EmployeeProfileForm, CustomUserChangeForm

# Helper function to check if a user is an Admin
def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

# Helper function to check if a user is a Manager or Admin
def is_manager_or_admin(user):
    return user.is_authenticated and (user.role == 'Manager' or user.role == 'Admin')

# Employee List View (Accessible by Admin and Manager)
@login_required
@user_passes_test(is_manager_or_admin)
def employee_list(request):
    employees = EmployeeProfile.objects.select_related('user').all().order_by('user__username')
    context = {'employees': employees}
    return render(request, 'employees/employee_list.html', context)

# Add Employee View (Accessible by Admin only)
@login_required
@user_passes_test(is_admin)
def employee_add(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = EmployeeProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic(): # Ensure both user and profile are saved or neither
                user = user_form.save() # Save the user first
                profile = profile_form.save(commit=False) # Don't save profile yet
                profile.user = user # Link the profile to the newly created user
                profile.save() # Now save the profile
            return redirect('employee_list')
    else:
        user_form = CustomUserCreationForm()
        profile_form = EmployeeProfileForm()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'form_title': 'Add New Employee'
    }
    return render(request, 'employees/employee_form.html', context)

@login_required
@user_passes_test(is_admin)
def employee_edit(request, pk):
    employee_profile = get_object_or_404(EmployeeProfile, pk=pk)
    user = employee_profile.user

    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=user)
        profile_form = EmployeeProfileForm(request.POST, instance=employee_profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            return redirect('employee_list')
    else:
        user_form = CustomUserChangeForm(instance=user)
        profile_form = EmployeeProfileForm(instance=employee_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'form_title': 'Edit Employee'
    }
    return render(request, 'employees/employee_form.html', context)

@login_required
@user_passes_test(is_admin)
def employee_delete(request, pk):
    employee_profile = get_object_or_404(EmployeeProfile, pk=pk)
    if request.method == 'POST':
        employee_profile.delete()
        return redirect('employee_list')
    context = {'employee': employee_profile}
    return render(request, 'employees/employee_confirm_delete.html', context)

@login_required
def dashboard(request):
    user_role = request.user.role
    context = {
        'user_role': user_role,
        'username': request.user.username,
    }
    return render(request, 'dashboard.html', context)

