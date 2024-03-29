
from pathlib import Path
import os
import environ

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / '.env')
SECRET_KEY=os.environ.get('SECRET_KEY')
STRIPE_PUBLIC_KEY_TEST=os.environ.get('STRIPE_PUBLIC_KEY_TEST')
STRIPE_SECRET_KEY_TEST=os.environ.get('STRIPE_SECRET_KEY_TEST')
STRIPE_WEBHOOK_SECRET_TEST=os.environ.get('STRIPE_WEBHOOK_SECRET_TEST')
PRODUCT_PRICE=os.environ.get('PRODUCT_PRICE')

MONGO_USER=os.environ.get('MONGO_USER')
MONGO_PASSWORD=os.environ.get('MONGO_PASSWORD')
MONGO_HOST=os.environ.get('MONGO_HOST')
MONGO_DB=os.environ.get('MONGO_DB')
MONGO_COLLECTION=os.environ.get('MONGO_COLLECTION')

AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME=os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME=os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

STABILITY_API_KEY=os.environ.get('STABILITY_API_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = "o8a))*u-$1+d(cry@qt)4nyabv*!ucflu#%v0%intv1uh*%qsu"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['https://flashapp-259af069f939.herokuapp.com/', '127.0.0.1']

# Celery Broker
#CELERY_BROKER_URL = os.environ.get('SECRET_REDIS_URI')  # or 'RedisSecretURI' if that's the name you've set
#CELERY_RESULT_BACKEND = os.environ.get('SECRET_REDIS_URI')
CELERY_BROKER_URL = "rediss://:pfd170e964fe8105dde2fd0fac039559bf91d01b6fdc2f7163485e8289e7a4e06@ec2-3-226-149-176.compute-1.amazonaws.com:16440?ssl_cert_reqs=CERT_NONE"   # or 'RedisSecretURI' if that's the name you've set
CELERY_RESULT_BACKEND = "rediss://:pfd170e964fe8105dde2fd0fac039559bf91d01b6fdc2f7163485e8289e7a4e06@ec2-3-226-149-176.compute-1.amazonaws.com:16440?ssl_cert_reqs=CERT_NONE" 

#https://devcenter.heroku.com/articles/ssl-endpoint#acquire-ssl-certificate
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#SSLIFY_DISABLE = True
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_users.apps.AppUsersConfig',
    #'user_payment.apps.UserPaymentConfig',
    #'edit_photo.apps.EditPhotoConfig',
    'flashcards.apps.FlashcardsConfig',
    'whitenoise.runserver_nostatic',
    'django_heroku',
    'django_on_heroku',
    'django_q',
    #'sslify.middleware.SSLifyMiddleware',
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
        'ENGINE': env('pgENGINE'),
        'NAME': env('pgNAME'),
        'USER': env('pgUSER'),
        'PASSWORD': env('pgPASSWORD'),
        'HOST': env('pgHOST'),
        'PORT': env('pgPORT'),
    }
}

## User model
AUTH_USER_MODEL = 'app_users.AppUser'

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
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

#STATIC_URL = '/static/'
#STATIC_URL = "https://%s.s3.amazonaws.com/" % AWS_STORAGE_BUCKET_NAME
#MEDIA_URL = '/media/'
#STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static')]
#MEDIA_ROOT = BASE_DIR / 'media'

USE_S3 = os.getenv('USE_S3') == 'TRUE'

if USE_S3:
    # AWS settings
    AWS_STORAGE_BUCKET_NAME = 'your-s3-bucket-name'  # make sure this is set
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    
    # S3 Static settings
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # S3 Public Media settings
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]


import django_heroku
django_heroku.settings(locals())

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIRECT_DOMAIN = 'http://127.0.0.1:8000'

Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 1,
    'timeout': 10000000,
    'retry': 100000000,
    'queue_limit': 2,
    'bulk': 10,
    'orm': 'default',
    'redis': os.getenv('REDIS_URL')  # Use Redis URL from the environment variable
}
pgENGINE='django.db.backends.postgresql'
pgNAME='dephaguq2mn933'
pgUSER='srkixmzithrred'
pgPASSWORD='66fbf45ef8db1409e2e67b57eb78fce8787793a512369ebf5b6e45fd18cdff29'
pgHOST='ec2-54-234-13-16.compute-1.amazonaws.com'
pgPORT='5432'

EDEN_AI_API_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiY2VhNGJiYzMtODdhMC00NjFlLWE2MzAtNzAyZWYzMmZiNjgxIiwidHlwZSI6ImFwaV90b2tlbiJ9.lMe4eAHqdIn0PFJSBfQV9ZDpEK6YM1vuotN4Wjf2QIM'