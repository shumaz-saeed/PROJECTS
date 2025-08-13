from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q # For complex queries
from django.http import FileResponse, Http404
from django.conf import settings # To access MEDIA_ROOT
import os # For path manipulation

from .models import Document
from .forms import DocumentForm
from employees.models import User, EmployeeProfile # Import User and EmployeeProfile for role/department checks

# Helper functions (copied from employees app for convenience, or you could put them in a common utility file)
def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

def is_manager_or_admin(user):
    return user.is_authenticated and (user.role == 'Manager' or user.role == 'Admin')

def is_employee(user):
    return user.is_authenticated and user.role == 'Employee'

# --- Document Views ---

@login_required
def document_list(request):
    # Filter documents based on user's role and department
    if is_admin(request.user):
        documents = Document.objects.all().order_by('-uploaded_at')
    else:
        # All users can see 'public' documents
        q_objects = Q(access_level='public')

        # Managers and Employees can also see 'private' documents for their department
        try:
            user_profile = request.user.employee_profile
            user_department = user_profile.department
            q_objects |= Q(access_level='private', department=user_department)
        except EmployeeProfile.DoesNotExist:
            # User might not have an employee profile yet (e.g., newly created admin)
            pass

        documents = Document.objects.filter(q_objects).order_by('-uploaded_at')

    context = {
        'documents': documents,
        'can_manage_documents': is_manager_or_admin(request.user) # Only managers/admins can add/edit/delete
    }
    return render(request, 'documents/document_list.html', context)

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can upload documents
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES) # Important: include request.FILES for file uploads
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()
    context = {'form': form, 'form_title': 'Upload New Document'}
    return render(request, 'documents/document_form.html', context)

@login_required
@user_passes_test(is_manager_or_admin) # Only managers/admins can edit documents
def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Further permission check: Only the uploader or an Admin can edit
    if not (document.uploaded_by == request.user or is_admin(request.user)):
        return redirect('document_list') # Or render a permission denied page

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document)
    context = {'form': form, 'form_title': f'Edit Document: {document.title}'}
    return render(request, 'documents/document_form.html', context)

@login_required
@user_passes_test(is_admin) # Only Admin can delete documents
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        # Delete the file from storage before deleting the database record
        if document.file:
            if os.path.exists(document.file.path):
                os.remove(document.file.path)
        document.delete()
        return redirect('document_list')
    context = {'document': document}
    return render(request, 'documents/document_confirm_delete.html', context)

@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Permission check for downloading:
    # Admin can download any.
    # Manager/Employee can download public documents.
    # Manager/Employee can download private documents if they are in the same department.
    can_download = False
    if is_admin(request.user):
        can_download = True
    elif document.access_level == 'public':
        can_download = True
    elif document.access_level == 'private':
        try:
            user_profile = request.user.employee_profile
            if user_profile.department == document.department:
                can_download = True
        except EmployeeProfile.DoesNotExist:
            pass # User has no profile, cannot access private docs

    if not can_download:
        raise Http404("You do not have permission to access this document.")

    # Serve the file
    file_path = document.file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=document.filename())
    else:
        raise Http404("Document file not found.")
