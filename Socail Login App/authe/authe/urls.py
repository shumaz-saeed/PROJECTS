"""
URL configuration for authe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView  # Import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect the root URL ('/') to your users:home view
    path('', RedirectView.as_view(pattern_name='users:home'), name='root_redirect'),

    # Include your custom users app URLs for other paths like /home/, /profile/, etc.
    path('', include('users.urls')),
]
