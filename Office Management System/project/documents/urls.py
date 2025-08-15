
from django.urls import path
from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'), # List all documents (filtered by role/department)
    path('upload/', views.document_upload, name='document_upload'), # Upload new document
    path('edit/<int:pk>/', views.document_edit, name='document_edit'), # Edit existing document
    path('delete/<int:pk>/', views.document_delete, name='document_delete'), # Delete document
    path('download/<int:pk>/', views.document_download, name='document_download'), # Download document
]
