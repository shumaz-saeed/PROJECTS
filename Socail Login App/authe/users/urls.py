# # authe/users/urls.py

# from django.urls import path
# from . import views

# app_name = 'users'

# urlpatterns = [
#     path('profile/', views.profile, name='profile'),
#     path('home/', views.home, name='home'), # Add a home view if not already present
    
#     # Custom Google OAuth URLs
#     path('oauth/google/login/', views.start_google_auth, name='google_login'),
#     path('oauth/google/callback/', views.google_callback, name='google_callback'),

#     # Custom GitHub OAuth URLs
#     path('oauth/github/login/', views.start_github_auth, name='github_login'),
#     path('oauth/github/callback/', views.github_callback, name='github_callback'),

#     # Custom Facebook OAuth URLs
#     path('oauth/facebook/login/', views.start_facebook_auth, name='facebook_login'),
#     path('oauth/facebook/callback/', views.facebook_callback, name='facebook_callback'),
# ]
# authe/users/urls.py

from django.urls import path
from . import views

app_name = 'users' # Namespace for your app's URLs

urlpatterns = [
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('account/logout/', views.custom_logout, name='account_logout'), # Custom logout URL
    
    # Custom Google OAuth URLs
    path('oauth/google/login/', views.start_google_auth, name='google_login'),
    path('oauth/google/callback/', views.google_callback, name='google_callback'),

    # Custom GitHub OAuth URLs
    path('oauth/github/login/', views.start_github_auth, name='github_login'),
    path('oauth/github/callback/', views.github_callback, name='github_callback'),

    # Custom Facebook OAuth URLs
    path('oauth/facebook/login/', views.start_facebook_auth, name='facebook_login'),
    path('oauth/facebook/callback/', views.facebook_callback, name='facebook_callback'),
]
