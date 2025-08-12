from django.urls import path
from . import views

urlpatterns = [
    path('', views.announcement_list, name='announcement_list'), 
    path('add/', views.announcement_add, name='announcement_add'), 
    path('edit/<int:pk>/', views.announcement_edit, name='announcement_edit'), 
    path('delete/<int:pk>/', views.announcement_delete, name='announcement_delete'), 
]
