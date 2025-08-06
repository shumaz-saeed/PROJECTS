from django.urls import path
from . import views

urlpatterns = [
    path('', views.asset_list, name='asset_list'), # List all assets (filtered by role)
    path('add/', views.asset_add, name='asset_add'), # Add new asset
    path('edit/<int:pk>/', views.asset_edit, name='asset_edit'), # Edit existing asset
    path('delete/<int:pk>/', views.asset_delete, name='asset_delete'), # Delete asset
]
