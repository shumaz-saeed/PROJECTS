from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q # For complex queries
from .models import Asset
from .forms import AssetForm
from employees.models import User # Import User model for role checks

# Helper functions (copied from employees app for convenience, or you could put them in a common utility file)
def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

def is_manager_or_admin(user):
    return user.is_authenticated and (user.role == 'Manager' or user.role == 'Admin')

def is_employee(user):
    return user.is_authenticated and user.role == 'Employee'

# --- Asset Views ---

@login_required
def asset_list(request):
    # Admin/Manager can see all assets
    # Employees can only see assets assigned to them, or available assets
    if is_admin(request.user) or is_manager_or_admin(request.user):
        assets = Asset.objects.all().order_by('name')
    else: # Employee
        assets = Asset.objects.filter(Q(assigned_to=request.user) | Q(status='available')).order_by('name')

    context = {
        'assets': assets,
        'can_manage_assets': is_admin(request.user) # Only Admin can add/edit/delete assets
    }
    return render(request, 'assets/asset_list.html', context)

@login_required
@user_passes_test(is_admin) # Only Admin can add assets
def asset_add(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm()
    context = {'form': form, 'form_title': 'Add New Asset'}
    return render(request, 'assets/asset_form.html', context)

@login_required
@user_passes_test(is_admin) # Only Admin can edit assets
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm(instance=asset)
    context = {'form': form, 'form_title': f'Edit Asset: {asset.name}'}
    return render(request, 'assets/asset_form.html', context)

@login_required
@user_passes_test(is_admin) 
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == 'POST':
        asset.delete()
        return redirect('asset_list')
    context = {'asset': asset}
    return render(request, 'assets/asset_confirm_delete.html', context)
