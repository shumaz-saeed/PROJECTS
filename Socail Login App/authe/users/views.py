# authe/users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout # Import authenticate, login, logout
from django.contrib.auth import get_user_model # To get the User model
from django.contrib import messages
from django.conf import settings
import requests
import json
from django.contrib.auth.decorators import login_required
from django.utils import timezone # Import timezone for datetime fields

from .models import UserProfile
from .forms import UserProfileForm

User = get_user_model() # Get the currently active User model

def home(request):
        """
        Renders the home page with social login options or user status.
        """
        return render(request, 'users/home.html')

@login_required
def profile(request):
        """
       Allows authenticated users to view and update their profile.
        """
        # Get or create UserProfile for the current user
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
                print(f"User {request.user.username}'s profile form saved successfully!")
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('users:profile') # Redirect back to profile after update
            else:
                print(f"Form validation failed for {request.user.username}'s profile.")
                messages.error(request, 'Please correct the errors below.')
        else:
            form = UserProfileForm(instance=user_profile)
            print(f"Form generated for user {request.user.username}.")

        return render(request, 'users/profile.html', {'form': form, 'profile': user_profile}) # Pass profile object to template

def custom_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return render(request, 'users/custom_logout.html')

    # --- Helper function to handle user login/creation from social data ---
def handle_social_user_login(request, email, username, first_name=None, last_name=None, 
                                 provider=None, provider_id=None, profile_picture=None,
                                 access_token=None, refresh_token=None):
        """
        Handles logging in an existing user or creating a new one based on social data.
        Ensures that if a user signs up once, they are logged in directly on subsequent attempts.
        Now also saves social provider details to UserProfile.
        """
        try:
            # 1. Check if a user with that email already exists
            user = User.objects.get(email=email)
            print(f"User with email {email} found. Logging in.")
            
            # Update existing user's profile with latest social data
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.provider = provider
            user_profile.provider_id = provider_id
            user_profile.profile_picture = profile_picture
            user_profile.access_token = access_token
            user_profile.refresh_token = refresh_token
            user_profile.last_login_provider = timezone.now() # Update last login time
            user_profile.save()
            print(f"Updated UserProfile for existing user {user.username}.")

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return True, user
        except User.DoesNotExist:
            # 2. If user does not exist, create a new user
            print(f"User with email {email} not found. Creating new user.")
            try:
                base_username = username.split('@')[0] if '@' in username else username
                new_username = base_username
                counter = 1
                while User.objects.filter(username=new_username).exists():
                    new_username = f"{base_username}{counter}"
                    counter += 1

                user = User.objects.create_user(
                    username=new_username,
                    email=email,
                    first_name=first_name if first_name else '',
                    last_name=last_name if last_name else '',
                    password=None # Use set_unusable_password() below
                )
                user.set_unusable_password() # Mark password as unusable for social logins
                user.save()
                print(f"New user {user.username} created.")

                # Create UserProfile for the new user and save social data
                UserProfile.objects.create(
                    user=user,
                    provider=provider,
                    provider_id=provider_id,
                    profile_picture=profile_picture,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    last_login_provider=timezone.now()
                )
                print(f"UserProfile created for {user.username} with social data.")

                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, f"Welcome, {user.username}! Your account has been created.")
                return True, user
            except Exception as e:
                print(f"Error creating new user: {e}")
                messages.error(request, f"Could not create account: {e}")
                return False, None
        except Exception as e:
            print(f"An unexpected error occurred during social login: {e}")
            messages.error(request, f"An error occurred during login: {e}")
            return False, None


    # --- Custom Social Login Functions (updated to pass more data) ---

def start_google_auth(request):
        """
        Initiates the Google OAuth 2.0 authorization flow.
        """
        google_client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
        redirect_uri = request.build_absolute_uri('/oauth/google/callback/')
        scope = "profile email"
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={google_client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"access_type=offline"
        )
        print(f"Redirecting to Google Auth URL: {auth_url}")
        return redirect(auth_url)

def google_callback(request):
        """
        Handles the Google OAuth 2.0 callback, exchanges code for token, and processes user data.
        """
        print("Google callback received.")
        code = request.GET.get('code')
        error = request.GET.get('error')

        if error:
            print(f"Google Auth Error: {error}")
            messages.error(request, f"Google login failed: {error}")
            return redirect('users:home')

        if not code:
            print("Google callback: No authorization code received.")
            messages.error(request, "Google login failed: No authorization code.")
            return redirect('users:home')

        google_client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
        google_client_secret = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret']
        redirect_uri = request.build_absolute_uri('/oauth/google/callback/')

        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': google_client_id,
            'client_secret': google_client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        print("Exchanging code for Google token...")
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' in token_json:
            access_token = token_json['access_token']
            refresh_token = token_json.get('refresh_token') # Get refresh token if available
            print(f"Google Access Token obtained: {access_token[:10]}...")

            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            userinfo_response = requests.get(userinfo_url, headers={'Authorization': f'Bearer {access_token}'})
            user_data = userinfo_response.json()
            print(f"Google User Data: {user_data}")

            email = user_data.get('email')
            name = user_data.get('name')
            given_name = user_data.get('given_name')
            family_name = user_data.get('family_name')
            profile_picture = user_data.get('picture') # Get profile picture URL
            provider_id = user_data.get('sub') # Google's unique user ID

            if not email:
                messages.error(request, "Google login failed: No email provided by Google.")
                return redirect('users:home')

            success, user = handle_social_user_login(
                request, email, name or email, given_name, family_name,
                provider='google', provider_id=provider_id, profile_picture=profile_picture,
                access_token=access_token, refresh_token=refresh_token
            )
            if success:
                return redirect('users:home')
            else:
                return redirect('users:home')

        else:
            print(f"Failed to get Google Access Token: {token_json.get('error_description', token_json)}")
            messages.error(request, f"Google login failed: {token_json.get('error_description', 'Unknown error')}")
            return redirect('users:home')


def start_github_auth(request):
        """
        Initiates the GitHub OAuth authorization flow.
        """
        github_client_id = settings.SOCIALACCOUNT_PROVIDERS['github']['APP']['client_id']
        redirect_uri = request.build_absolute_uri('/oauth/github/callback/')
        scope = "user:email"
        auth_url = (
            f"https://github.com/login/oauth/authorize?"
            f"client_id={github_client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}"
        )
        print(f"Redirecting to GitHub Auth URL: {auth_url}")
        return redirect(auth_url)

def github_callback(request):
        """
        Handles the GitHub OAuth callback, exchanges code for token, and processes user data.
        """
        print("GitHub callback received.")
        code = request.GET.get('code')
        error = request.GET.get('error')

        if error:
            print(f"GitHub Auth Error: {error}")
            messages.error(request, f"GitHub login failed: {error}")
            return redirect('users:home')

        if not code:
            print("GitHub callback: No authorization code received.")
            messages.error(request, "GitHub login failed: No authorization code.")
            return redirect('users:home')

        github_client_id = settings.SOCIALACCOUNT_PROVIDERS['github']['APP']['client_id']
        github_client_secret = settings.SOCIALACCOUNT_PROVIDERS['github']['APP']['secret']
        redirect_uri = request.build_absolute_uri('/oauth/github/callback/')

        token_url = "https://github.com/login/oauth/access_token"
        token_data = {
            'client_id': github_client_id,
            'client_secret': github_client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
        }
        headers = {'Accept': 'application/json'}
        print("Exchanging code for GitHub token...")
        token_response = requests.post(token_url, data=token_data, headers=headers)
        token_json = token_response.json()

        if 'access_token' in token_json:
            access_token = token_json['access_token']
            print(f"GitHub Access Token obtained: {access_token[:10]}...")

            userinfo_url = "https://api.github.com/user"
            userinfo_response = requests.get(userinfo_url, headers={'Authorization': f'token {access_token}'})
            user_data = userinfo_response.json()
            print(f"GitHub User Data: {user_data}")

            email = user_data.get('email')
            username = user_data.get('login')
            name = user_data.get('name')
            profile_picture = user_data.get('avatar_url') # GitHub's profile picture URL
            provider_id = str(user_data.get('id')) # GitHub's unique user ID

            if not email:
                emails_url = "https://api.github.com/user/emails"
                emails_response = requests.get(emails_url, headers={'Authorization': f'token {access_token}'})
                emails_data = emails_response.json()
                for email_entry in emails_data:
                    if email_entry.get('primary') and email_entry.get('verified'):
                        email = email_entry.get('email')
                        break
                if not email:
                    messages.error(request, "GitHub login failed: No primary verified email found.")
                    return redirect('users:home')

            success, user = handle_social_user_login(
                request, email, username, name, None,
                provider='github', provider_id=provider_id, profile_picture=profile_picture,
                access_token=access_token
            )
            if success:
                return redirect('users:home')
            else:
                return redirect('users:home')

        else:
            print(f"Failed to get GitHub Access Token: {token_json.get('error', token_json)}")
            messages.error(request, f"GitHub login failed: {token_json.get('error', 'Unknown error')}")
            return redirect('users:home')


def start_facebook_auth(request):
        """
        Initiates the Facebook OAuth authorization flow.
        """
        facebook_app_id = settings.SOCIALACCOUNT_PROVIDERS['facebook']['APP']['client_id']
        redirect_uri = request.build_absolute_uri('/oauth/facebook/callback/')
        scope = "email,public_profile"
        auth_url = (
            f"https://www.facebook.com/v19.0/dialog/oauth?"
            f"client_id={facebook_app_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={scope}"
        )
        print(f"Redirecting to Facebook Auth URL: {auth_url}")
        return redirect(auth_url)

def facebook_callback(request):
        """
        Handles the Facebook OAuth callback, exchanges code for token, and processes user data.
        """
        print("Facebook callback received.")
        code = request.GET.get('code')
        error = request.GET.get('error')

        if error:
            print(f"Facebook Auth Error: {error}")
            messages.error(request, f"Facebook login failed: {error}")
            return redirect('users:home')

        if not code:
            print("Facebook callback: No authorization code received.")
            messages.error(request, "Facebook login failed: No authorization code.")
            return redirect('users:home')

        facebook_app_id = settings.SOCIALACCOUNT_PROVIDERS['facebook']['APP']['client_id']
        facebook_app_secret = settings.SOCIALACCOUNT_PROVIDERS['facebook']['APP']['secret']
        redirect_uri = request.build_absolute_uri('/oauth/facebook/callback/')

        token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
        token_data = {
            'client_id': facebook_app_id,
            'client_secret': facebook_app_secret,
            'code': code,
            'redirect_uri': redirect_uri,
        }
        print("Exchanging code for Facebook token...")
        token_response = requests.get(token_url, params=token_data)
        token_json = token_response.json()

        if 'access_token' in token_json:
            access_token = token_json['access_token']
            print(f"Facebook Access Token obtained: {access_token[:10]}...")

            userinfo_url = f"https://graph.facebook.com/v19.0/me?fields=id,name,email&access_token={access_token}"
            userinfo_response = requests.get(userinfo_url)
            user_data = userinfo_response.json()
            print(f"Facebook User Data: {user_data}")

            email = user_data.get('email')
            name = user_data.get('name')
            # Facebook often provides full name, not separate first/last name easily without additional fields/permissions

            if not email:
                messages.error(request, "Facebook login failed: No email provided by Facebook. Ensure 'email' scope is approved.")
                return redirect('users:home')

            success, user = handle_social_user_login(request, email, name or email, name, None)
            if success:
                return redirect('users:home')
            else:
                return redirect('users:home')

        else:
            print(f"Failed to get Facebook Access Token: {token_json.get('error_description', token_json)}")
            messages.error(request, f"Facebook login failed: {token_json.get('error_description', 'Unknown error')}")
            return redirect('users:home')

