"""
Django settings for coursegenie project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sf#(b=^nfm$8@1fiqi2qvmp&ot-5(zat=+twv8$50d^29cayp#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('ENV', 'development') == 'development'

ALLOWED_HOSTS = ['localhost']
if 'DJANGO_HOST' in os.environ:
    ALLOWED_HOSTS.append(os.environ['DJANGO_HOST'])

if 'CLOUDFLARE' in os.environ:
    # CloudFlare forwarding enabled
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Installed Applications
    'django_cas_ng',
    'rest_framework',
    'cacheops',

    # Custom applications
    'core',
    'api',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        #'rest_framework.permissions.IsAdminUser',
        'rest_framework.permissions.AllowAny',
    ],
    'PAGE_SIZE': 10
}

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # CAS (Central Authentication Service) Middleware
    'django_cas_ng.middleware.CASMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
]

ROOT_URLCONF = 'coursegenie.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'coursegenie.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

import dj_database_url
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

# Cache Configuration
REDIS_URL = os.environ.get('REDIS_URL', '')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '%s/cache' % REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        },
    }

CACHEOPS_REDIS = '%s/cacheops' % REDIS_URL
CACHEOPS_DEFAULTS = {'timeout': 60*15}
CACHEOPS = {
    # local_get allows the caching to occur in-memory on the Python side, which
    # is still faster than hitting the Redis cache. Should *only* happen for
    # data that never changes (i.e. loaded requirement data).
    'core.Degree': {'ops': 'all', 'local_get': True},
    'core.Major': {'ops': 'all', 'local_get': True},
    'core.Certificate': {'ops': 'all', 'local_get': True},
    'core.Track': {'ops': 'all', 'local_get': True},
    'core.Course': {'ops': 'all', 'local_get': True},
    'core.CrossListing': {'ops': 'all', 'local_get': True},
    'core.Requirement': {'ops': 'all', 'local_get': True},
    'core.NestedReq': {'ops': 'all', 'local_get': True},
    }
CACHEOPS_DEGRADE_ON_FAILURE = True

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, os.environ.get('STATIC_ROOT', '_static'))
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Installed Application Configuration
CAS_SERVER_URL = os.environ.get('CAS_URL')
TRANSCRIPT_API_URL = os.environ.get('TRANSCRIPT_API_URL')
