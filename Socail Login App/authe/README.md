
# 🚀 authe: Django Social Authentication Starter
authe is a robust and customizable Django project designed to provide seamless social authentication using Google, GitHub, and Facebook. This project serves as a comprehensive starter kit for developers who want to integrate third-party login options into their Django applications with full control over the authentication flow.

Instead of relying on external packages like django-allauth, this project features a clean, custom implementation of the OAuth 2.0 protocol. This gives you a deeper understanding of the authentication process while leveraging Django's built-in User model and a custom UserProfile for extended data.

## ✨ Features
Custom OAuth 2.0 Implementation: Direct integration with Google, GitHub, and Facebook OAuth APIs.

Django User Model: Seamlessly leverages Django's native User model for core authentication.

Extended User Profiles: A custom UserProfile model stores additional data like a bio, website, and social provider details (e.g., provider name, ID, and tokens).

Responsive UI: A clean and modern user interface is built with Tailwind CSS, ensuring a great look on all devices.

PostgreSQL Database: Configured for robust and scalable data persistence.

Secure Configuration: Securely manages API keys and secrets using python-dotenv.

Session-based Authentication: Standard Django session management handles authenticated users.

User-Friendly Messaging: Utilizes Django's messages framework for clear user feedback.

## 🛠️ Technologies Used
Django 5.x: Web Framework

Python 3.x: Programming Language

PostgreSQL: Database

Requests: HTTP library for API interactions

python-dotenv: Environment variable management

Tailwind CSS: For styling and responsive design

## 🚀 Getting Started
Follow these steps to get your authe project up and running locally.

Prerequisites
Before you begin, ensure you have:

Python 3.x installed

pip (Python package installer)

PostgreSQL installed and running

1. Clone the Repository
Bash

git clone https://github.com/your-username/authe.git # Replace with your actual repo URL
cd authe
2. Create a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.

Bash

python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
3. Install Dependencies
Bash

pip install django requests psycopg2-binary python-dotenv
4. PostgreSQL Database Setup
Ensure your PostgreSQL server is running. Then, create a database and a user that match the settings in authe/authe/settings.py.

Example (using psql):

SQL

CREATE DATABASE authe_db; -- Or whatever name you set in settings.py
CREATE USER authe_user WITH PASSWORD 'your_password'; -- Use a strong password
ALTER ROLE authe_user SET client_encoding TO 'utf8';
ALTER ROLE authe_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE authe_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE authe_db TO authe_user;
Update authe/authe/settings.py with your database credentials:

Python

# authe/authe/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'authe_db',          # Your PostgreSQL database name
        'USER': 'authe_user',        # Your PostgreSQL username
        'PASSWORD': 'your_password', # Your PostgreSQL password
        'HOST': 'localhost',         # Where PostgreSQL is running
        'PORT': '5432',              # Default PostgreSQL port
    }
}
5. Configure Social API Credentials
You need to register your application with each provider to obtain a client_id and client_secret.

Google: Google Cloud Console (OAuth 2.0 Client IDs for Web application)

GitHub: GitHub Developer Settings (OAuth Apps)

Facebook: Facebook for Developers (Facebook Login)

Important Redirect URIs:
For local development, set the following Authorized Redirect URIs in your respective provider's developer console:

Google: http://127.0.0.1:8000/oauth/google/callback/

GitHub: http://127.0.0.1:8000/oauth/github/callback/

Facebook: http://127.0.0.1:8000/oauth/facebook/callback/

Create a .env file in the root of your project (next to manage.py) and add your credentials:

Bash

# .env
GOOGLE_CLIENT_ID='YOUR_GOOGLE_CLIENT_ID'
GOOGLE_CLIENT_SECRET='YOUR_GOOGLE_CLIENT_SECRET'
FACEBOOK_CLIENT_ID='YOUR_FACEBOOK_APP_ID'
FACEBOOK_CLIENT_SECRET='YOUR_FACEBOOK_APP_SECRET'
GITHUB_CLIENT_ID='YOUR_GITHUB_CLIENT_ID'
GITHUB_CLIENT_SECRET='YOUR_GITHUB_CLIENT_SECRET'
6. Run Migrations
Apply the database schema changes:

Bash

python manage.py makemigrations users
python manage.py migrate
7. Create a Superuser (Optional)
Bash

python manage.py createsuperuser
Follow the prompts to create an admin user.

8. Run the Development Server
Bash

python manage.py runserver
Open your web browser and navigate to: http://127.0.0.1:8000/

## 📖 Usage
Home Page (/ or /home/): Provides links to log in with social accounts.

Social Login: Clicking a social provider button initiates the OAuth flow, after which you'll be redirected and logged in.

Profile Page (/profile/): Displays your user details and allows you to update your profile.

Logout (/logout/): Logs you out and shows a confirmation message.

## 📂 Project Structure
authe/
├── authe/                   # Main project directory
│   ├── settings.py          # Project settings (updated for PostgreSQL, social API keys)
│   ├── urls.py              # Main URL configuration
├── users/                   # Your custom users application
│   ├── migrations/
│   ├── models.py            # Defines UserProfile model
│   ├── urls.py              # App-specific URL patterns for social auth and profile
│   └── views.py             # Logic for social auth, profile, home, logout
│   └── templates/
│       └── users/
│           ├── home.html    # Landing page with social login buttons
│           ├── profile.html # User profile page
├── manage.py                # Django's command-line utility
└── .env                     # Environment variables (client IDs, secrets)
