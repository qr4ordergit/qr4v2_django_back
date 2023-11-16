from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'authenticator',
    'api',

     # ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.amazon',
    # ...
]


# Cognito User Pool Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") #'your_access_key'
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") #'your_secret_key'
AWS_REGION = os.getenv("AWS_REGION") #'YOUR_AWS_REGION'
COGNITO_USER_POOL_ID =  os.getenv("COGNITO_USER_POOL_ID") #'YOUR_USER_POOL_ID'
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID") # 'YOUR_CLIENT_ID'


AUTHENTICATION_BACKENDS = [
    # ...
    'allauth.account.auth_backends.AuthenticationBackend',
    # ...
]


SITE_ID = 1

ACCOUNT_EMAIL_VERIFICATION = 'none'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'qr4order.urls'

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

WSGI_APPLICATION = 'qr4order.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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

USE_L10N = True


USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('en-us',_('English')),
    # ('th',_('Thailand')),
    # ('ja',_('Japanese')),
    # ('ko',_('Korean')),
    # ('it',_('Italian')),
    # ('zh-hans',_('Chinese Simplified')),
    ('ro',_('Romanian')),
    ('ua',_('Ukrainian'))
]
