"""
Django settings for PlatformDemonList project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta

import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = os.path.join(BASE_DIR, 'apps')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!ms2$8xk0yav_764y^xkt8calhmk)#a1n4&&m!i0)2gbq#myym'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'platformerlist.uc.r.appspot.com', 'www.platformerlist.uc.r.appspot.com']

# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'background_task',
    "django_filters",
    'django_recaptcha',
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt"
)

LOCAL_APPS = (
    'apps.demonlist.apps.DemonlistConfig',
    'apps.users.apps.UsersConfig',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'PlatformDemonList.middleware.RedirectMiddleware',
    'PlatformDemonList.middleware.CustomAuthMiddleware',
    'PlatformDemonList.middleware.MethodOverrideMiddleware',
    'PlatformDemonList.middleware.GlobalContextMiddleware',
    'allauth.account.middleware.AccountMiddleware'
]

ROOT_URLCONF = 'PlatformDemonList.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
                'my_templatetag': 'apps.demonlist.templatetags.custom_tags',
                }
        },
    },
]

ASGI_APPLICATION = 'PlatformDemonList.asgi.application'

WSGI_APPLICATION = 'PlatformDemonList.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'demonlist_refactor',
        'USER': 'postgres',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'demonlist',
        'USER': 'super',
        'PASSWORD': 'BXsW#RGvF2PYdy6',
        'HOST': '127.0.0.1',
        'PORT': '9999'
    }
}"""

DATABASES['default']['ATOMIC_REQUESTS'] = False


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '..', 'static'),
)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media')
#MEDIA_URL = 'https://www.demonlist.com/media/'
MEDIA_URL = '/media/'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = LOGIN_URL

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '465'
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'thegeomaxteam@gmail.com'
EMAIL_HOST_PASSWORD = 'zpairtkaedcfrids'

RECAPTCHA_PUBLIC_KEY = '6Leh_iMqAAAAAGDu80kZ40hVFxhDtAaDBVVwk3L8'
RECAPTCHA_PRIVATE_KEY = '6Leh_iMqAAAAAA6Kj6cP3ImA6USGMwJXLc4hK1cL'

# Security
#CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'


# Admin
ADMIN_URL = 'admin/'
ADMINS = [
    ("""ChuckyGD""", 'ChuckyGD'),
]
MANAGERS = ADMINS

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=365*100),  # 100 years expiration
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365*100),  # 100 years expiration
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=365*100),  # 100 years expiration
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=365*100),  # 100 years expiration
}

# Set the access token expiration to a very large value in seconds
ACCESS_TOKEN_EXPIRATION = 3600 * 24 * 365 * 100  # 100 years in seconds


# Las 'CATEGORIES' son todas las categorías disponibles en la página web (para el order position)
CATEGORIES = ["rated", "unrated", "challenge", "shitty", "future", "tiny", "deathless", "impossible", "spam", "impossible_tiny", "all"]

# Las 'ALTERNATIVE_CATEGORIES' son las categorías sin rated y unrated
ALTERNATIVE_CATEGORIES = CATEGORIES[2:]
