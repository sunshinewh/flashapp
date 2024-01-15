"""
Django settings for django_examples project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "o8a))*u-$1+d(cry@qt)4nyabv*!ucflu#%v0%intv1uh*%qsu"
STRIPE_PUBLIC_KEY_TEST='pk_test_12345...'
STRIPE_SECRET_KEY_TEST='sk_test_12345...'
STRIPE_WEBHOOK_SECRET_TEST='whsec_12345..'
PRODUCT_PRICE='price_12345...'

MONGO_USER='user'
MONGO_PASSWORD='KJLhK8rwgYKYMpcGr6v4'
MONGO_HOST='cluster0.sirwuvv.mongodb.net'
MONGO_DB='flashcard_db'
MONGO_COLLECTION='cards'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['https://flashapp-259af069f939.herokuapp.com/', '127.0.0.1']

## rabbitmq message broker for Celery
CELERY_BROKER_URL = 'pyamqp://127.0.0.1:5672'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_users.apps.AppUsersConfig',
    'user_payment.apps.UserPaymentConfig',
    'edit_photo.apps.EditPhotoConfig',
    'flashcards.apps.FlashcardsConfig',
    'whitenoise.runserver_nostatic',
    'django_heroku',
    'django_on_heroku',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
]

ROOT_URLCONF = 'django_examples.urls'

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_examples.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgres',
        'NAME': 'dephaguq2mn933',
        'USER': 'srkixmzithrred',
        'PASSWORD': '66fbf45ef8db1409e2e67b57eb78fce8787793a512369ebf5b6e45fd18cdff29',
        'HOST': 'ec2-54-234-13-16.compute-1.amazonaws.com'
        'PORT': '5432'
    }
}

## User model
AUTH_USER_MODEL = 'app_users.AppUser'


# MongoDB
# flashcard app

# MONGO DB
#MONGO_USER='user'
#MONGO_PASSWORD='KJLhK8rwgYKYMpcGr6v4'
#MONGO_HOST='mongodb+srv://user:KJLhK8rwgYKYMpcGr6v4@cluster0.sirwuvv.mongodb.net'
#MONGO_DB='flashcard_db'
#MONGO_COLLECTION='cards'    


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
#STATICFILES_DIRS = [ BASE_DIR / 'static' ]
STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static')]
# Media files
#SMEDIA_URL = '/media/'
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'


#STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

import django_heroku
django_heroku.settings(locals())

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

## Stripe
STRIPE_PUBLIC_KEY_TEST = os.getenv('STRIPE_PUBLIC_KEY_TEST')
STRIPE_SECRET_KEY_TEST = os.getenv('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET_TEST = os.getenv('STRIPE_WEBHOOK_SECRET_TEST')
PRODUCT_PRICE = os.getenv('PRODUCT_PRICE')

REDIRECT_DOMAIN = 'http://127.0.0.1:8000'
