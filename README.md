# News Platform Project
Overview

This project is a news platform built with Django, designed to allow readers, journalists, editors, and managers to interact with news content. It includes role-based dashboards, article and newsletter management, subscription-based access, and an API for reading articles.

# Features
## User Roles

- Reader: Can subscribe to publishers and journalists, view approved articles and newsletters.
- Journalist: Can create articles and newsletters, manage content they authored.
- Editor: Can approve or edit articles and newsletters from their publisher.
- Manager: Can create and manage publishers.

## Core Functionality
- CRUD operations for articles, newsletters, and publishers.
- Subscription system for readers to follow publishers or journalists.
- Role-based dashboards for each type of user.
- Email-based password reset system with tokens.
- API endpoints for retrieving approved articles and user subscriptions.
- Permissions enforcement using groups, decorators, and DRF permissions.

# Tech Stack
- Backend: Django 5.x
- Database: SQLite to work with docker
- Frontend: Django Templates + Bootstrap 5
- API: Django REST Framework
- Authentication: Django custom user model with roles
- Email: Django Email backend (SMTP)

# Installation
## Prerequisites
- Python 3.11+
- pip (Python package manager)

# Setting Up
- Clone the repository
- Navigate into the directory:
    - cd Task

- Create a virtual enviroment to install dependancies:
  - python -m venv venv

- Activate enviroment:
  - source venv/bin/activate # macOS/Linux
  - venv\Scripts\activate # Windows

- Install dependancies:
  - pip install -r requirements.txt

# Update newsApp/settings.py database configuration to match your MySQL instance or MariaDB if you are not running with docker
1. MySQL Setup
    Install MySQL (if not installed):
        On Windows, download the installer from https://dev.mysql.com/downloads/mysql/
    
    Login to MySQL:
        mysql -u root -p

    Create the database:
        Create the database:

    Create a database user (replace <username> and <password>):
        CREATE USER '<username>'@'localhost' IDENTIFIED BY '<password>';
        GRANT ALL PRIVILEGES ON news_platform.* TO '<username>'@'localhost';
        FLUSH PRIVILEGES;

    Update Django settings (newsApp/settings.py):
        DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'news_app',
            'USER': '<username>', (root username)
            'PASSWORD': '<password>', (root password)
            'HOST': 'localhost',
            'PORT': '3307', (or whatever your port is)
        }
    }

2. MariaDB Setup
    - Install MariaDB:
        On Windows, download from https://mariadb.org/download/
    
    - Login to MariaDB:
        sudo mariadb

    - Create the database:
        CREATE DATABASE news_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

    - Create a user:
        CREATE USER '<username>'@'localhost' IDENTIFIED BY '<password>';
        GRANT ALL PRIVILEGES ON news_platform.* TO '<username>'@'localhost';
        FLUSH PRIVILEGES;
     
    - Update Django settings (newsApp/settings.py):
        DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'news_app',
            'USER': '<username>', (root username)
            'PASSWORD': '<password>', (root password)
            'HOST': 'localhost',
            'PORT': '3307', (or whatever your port is)
        }
    }









# Create a superuser

python manage.py createsuperuser

- Then follow the instructions on console, on what information to fill out

# ✉️ Email Setup (for password reset & order confirmation) (OPTIONAL), you can leave it, if you want to use my gmail acocunt

Update the settings.py:
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "your-app-password"

# Start the server

python manage.py runserver
Open your browser and go to http://127.0.0.1:8000

# Project Structure

Task/
│
├── accounts/             # User management, authentication, forms, and signals
├── news/                 # Core app for articles, newsletters, publishers
├── api/                  # Django REST Framework API endpoints
├── decorators/           # Custom Decorators
├── helpers/              # Custom helper methods
├── newsApp/              # Project level files and settings
├── Planning/             # Project Planning
├── templates/            # HTML templates for dashboards and forms
├── static/               # CSS, JS, and media assets
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation


# API Endpoints
- Articles
GET /api/articles/ → List approved articles based on reader subscriptions.
Permissions: Reader only.

- Subscriptions
GET /api/my-subscriptions/ → List the user's subscribed publishers and journalists.
Permissions: Reader only.


# Roles & Permissions
- Uses Django Groups for access control.
- Groups are automatically created when a user is registered:
    Reader
    Journalist
    Editor
    Manage_Publishers

- Permissions:
    Readers can view articles and newsletters to journalists and publishers they are subscribed to.
    Journalists can create, edit, and delete their articles/newsletters.
    Editors can approve/edit/delete content within their publishers.
    Managers can manage publishers.

# Notes
Password reset tokens expire in 5 minutes.
Independent articles/newsletters cannot be linked to a publisher.
Database used: MySQL, but will ruin perfectly fine with MariaDB.


# How to use & run the application
- Create a Superuser
    A superuser manages publishers and assigns journalists/editors either from /admin site or loggin in the application with superuser credentials
    will allow you to manage publishers, this is extra functionality i added.

    python manage.py createsuperuser
    Follow the prompts to set username, email, and password.
    Once created, log in to the /admin/ site or the application itself.

    etup Publishers and Users

    Create Publishers:
        Recommended via the application: /news/admins/create-publisher/
        Alternatively, use Django admin.

        Create Users:
        Create at least 2 of each role: Reader, Journalist, Editor.
        Use /admin/ site or a registration form (if enabled).
        Assign Journalists & Editors to Publishers:
        Login as superuser.
        Assign users to publishers via the application or admin panel.
        This ensures articles are properly linked to publishers.

    Creating Articles
        Journalists Workflow:
        Login as a journalist.
        Go to the create article page.
        Choose one of the following:
        Independent article (not linked to any publisher)
        Publisher article (must belong to a publisher the journalist is assigned to)
        Submit the article.
        Independent articles are automatically available.
        Publisher articles remain pending approval.

        Editors Workflow:
        Any editor assigned to the publisher can:
        View pending articles for their publisher.
        Edit or approve them.

        Once approved:
        Publisher subscribers receive an email notification.
        The approved article is also posted to X (Twitter).

    Reader Workflow
        Login as a reader.
        Subscribe to:
        Publishers
        Journalists

        Dashboard:
        Shows articles and newsletters from subscribed sources only.
        If no subscriptions exist, no content is displayed.

        Navigation:
        Articles: View all articles from subscriptions.
        Newsletters: View newsletters from subscriptions.
        Subscribe: Browse publishers/journalists to subscribe.

        Quick Guide to Access Articles:
        Articles appear on the reader dashboard after subscription.
        Clicking an article opens the full content.
        Newsletters aggregate multiple articles and are accessible via the “Newsletters” link.
        Unsubscribed readers will not see any content until subscriptions are made.

    Sending Emails and X Posts
        Approved publisher articles trigger:
        Email notifications to all publisher subscribed readers.
        X post for social media sharing.

    App urls:    
        Access the application at: http://127.0.0.1:8000/
        Admin panel: http://127.0.0.1:8000/admin/

# Important:
The Twitter account used in this project has been suspended during testing.
To test Twitter integration yourself, you must provide your own Twitter Developer App tokens and secrets in the twitter/twitter_client.py at the top of the file, in its variables

- CONSUMER_KEY = 'your_consumer_key'
- CONSUMER_SECRET = 'your_consumer_secret'
- ACCESS_KEY = 'your_access_token'
- ACCESS_SECRET = 'your_access_secret'

Only one authenticated instance is created at app runtime (singleton pattern). This ensures you authenticate once, and all subsequent posts reuse the same credentials.

Please view a picture called Proof Of Suspension.PNG, to see the message at the bottom of the picture showing
my account is currently suspended


# Running with Docker
- Build the Docker image:
    Run: docker run -p 8000:8000 news-app

- Run the Docker container:
    Run: docker run -p 8000:8000 news-app
    The container automatically runs migrations and starts the Django server.
    Access the app at http://localhost:8000
