from django.urls import path
from . import views

urlpatterns = [
    # Project URLs
    path('', views.project_list, name='project_list'), # List all projects
    path('add/', views.project_add, name='project_add'), # Add new project
    path('edit/<int:pk>/', views.project_edit, name='project_edit'), # Edit existing project
    path('delete/<int:pk>/', views.project_delete, name='project_delete'), # Delete project

    # Task URLs
    path('tasks/', views.task_list, name='task_list'), # List all tasks
    path('tasks/add/', views.task_add, name='task_add'), # Add new task
    path('tasks/edit/<int:pk>/', views.task_edit, name='task_edit'), # Edit existing task
    path('tasks/delete/<int:pk>/', views.task_delete, name='task_delete'), # Delete task
]
