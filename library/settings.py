import os
import pymysql
from pathlib import Path
from dotenv import load_dotenv

# 1. Database Trick for Cloud
pymysql.install_as_MySQLdb()

# 2. Load .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-123')

# Set to False for production, True for local debugging
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'libwebb', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Essential for Render/Vercel
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'library.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'library.wsgi.application'

# 5. Database Configuration (Aiven Cloud MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'defaultdb',
        'USER': 'avnadmin',
        'PASSWORD': os.getenv('DB_PASSWORD'), 
        'HOST': 'mysql-2f3f44fb-athulkrish36-84f9.a.aivencloud.com',
        'PORT': '24860',
        'OPTIONS': {
            # SSL logic: Uses cert locally, bypasses on Render/Vercel
            'ssl': {'ca': None} if os.getenv('RENDER') or os.getenv('VERCEL') else {'ca': os.path.join(BASE_DIR, 'ca-certificate.crt')},
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 6. Static Files (THE FIX FOR YOUR IMAGES)
STATIC_URL = '/static/'

# This tells Django where to find your images inside libwebb
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'libwebb', 'static'),
]

# This is where all files are gathered during 'collectstatic'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use 'CompressedStaticFilesStorage' - it's much more forgiving than 'Manifest'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'