from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from employees.models import User # Import User model for role checks

# Helper functions (copied from employees app for convenience, or you could put them in a common utility file)
def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

def is_manager_or_admin(user):
    return user.is_authenticated and (user.role == 'Manager' or user.role == 'Admin')

def is_employee(user):
    return user.is_authenticated and user.role == 'Employee'

# --- Project Views ---

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can manage projects
def project_list(request):
    projects = Project.objects.all().order_by('name')
    context = {
        'projects': projects,
        'is_manager_or_admin': is_manager_or_admin(request.user)
    }
    return render(request, 'projects/project_list.html', context)

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can add projects
def project_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    context = {'form': form, 'form_title': 'Create New Project'}
    return render(request, 'projects/project_form.html', context)

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can edit projects
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    context = {'form': form, 'form_title': f'Edit Project: {project.name}'}
    return render(request, 'projects/project_form.html', context)

@login_required
@user_passes_test(is_admin) # Only admin can delete projects
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    context = {'project': project}
    return render(request, 'projects/project_confirm_delete.html', context)


# --- Task Views ---

@login_required
def task_list(request):
    if is_admin(request.user) or is_manager_or_admin(request.user):
        # Admin/Manager sees all tasks
        tasks = Task.objects.select_related('project', 'assigned_to').all().order_by('deadline', 'priority')
    else:
        # Employee sees only tasks assigned to them
        tasks = Task.objects.filter(assigned_to=request.user).select_related('project', 'assigned_to').order_by('deadline', 'priority')

    context = {
        'tasks': tasks,
        'is_manager_or_admin': is_manager_or_admin(request.user)
    }
    return render(request, 'projects/task_list.html', context)

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can add tasks
def task_add(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    context = {'form': form, 'form_title': 'Create New Task'}
    return render(request, 'projects/task_form.html', context)

@login_required
@user_passes_test(lambda u: is_manager_or_admin(u) or u.tasks.filter(pk=u.resolver_match.kwargs['pk']).exists()) # Manager/Admin OR assigned employee
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Permission check: Only manager/admin or the assigned employee can edit
    if not (is_manager_or_admin(request.user) or task.assigned_to == request.user):
        return redirect('task_list') # Or render a permission denied page

    if request.method == 'POST':
        # If not admin/manager, restrict status change if task is not assigned to them
        if not is_manager_or_admin(request.user) and task.assigned_to != request.user:
            # If an employee is trying to edit a task not assigned to them, only allow specific fields.
            # For simplicity, we'll just prevent saving for now.
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                # Prevent changing assigned_to or project by non-admin/manager
                if form.has_changed() and ('assigned_to' in form.changed_data or 'project' in form.changed_data):
                    if not is_admin(request.user): # Only admin can change assigned_to/project
                        form.add_error(None, "You do not have permission to change the assigned employee or project.")
                    else:
                        form.save()
                        return redirect('task_list')
                else:
                    form.save()
                    return redirect('task_list')
        else: # Admin/Manager or assigned employee editing their own task
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    context = {'form': form, 'form_title': f'Edit Task: {task.title}'}
    return render(request, 'projects/task_form.html', context)


@login_required
@user_passes_test(is_admin) # Only admin can delete tasks
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    context = {'task': task}
    return render(request, 'projects/task_confirm_delete.html', context)
