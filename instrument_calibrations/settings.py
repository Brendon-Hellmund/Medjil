"""
Django settings for InstrumentCalibration project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'd%t^naj(!0x3-te!aq@gt=2wze9^oqs=3)k3$_(ng7c4d8bk_%'
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY: 
    SECRET_KEY = 'd%t^naj(!0x3-te!aq@gt=2wze9^oqs=3)k3$_(ng7c4d8bk_%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DEBUG', default=0))
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']
# ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')
CSRF_TRUSTED_ORIGINS = ['http://localhost:1337', 'http://127.0.0.1:8000']

# Add Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    # 'crispy_forms',
    'formtools',
    'accounts',
    'backcapture',
    'calibrationsites',
    'instruments',
    'rangecalibration',
    'staffcalibration',
    'baseline_calibration',
    'edm_calibration',
    'calibrationguide',
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

ROOT_URLCONF = 'instrument_calibrations.urls'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'instrument_calibrations.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if 'SQL_ENGINE' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('SQL_ENGINE'),
            'NAME': os.environ.get('SQL_DATABASE'),
            'USER': os.environ.get('SQL_USER'),
            'PASSWORD': os.environ.get('SQL_PASSWORD'),
            'HOST': os.environ.get('SQL_HOST'),
            'PORT': os.environ.get('SQL_PORT'),

        }
    } 
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

#DJANG MESSAGE
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    
    {   'NAME': 'instrument_calibrations.passwordValidators.NumberValidator',
        'OPTIONS': {
            'min_digits': 1, 
            }
    },
    {'NAME': 'instrument_calibrations.passwordValidators.UppercaseValidator', },
    {'NAME': 'instrument_calibrations.passwordValidators.LowercaseValidator', },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
DATE_INPUT_FORMATS = ('%d-%m-%Y','%Y-%m-%d')
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'assets'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

#SECURITY SETTINGS
#CSRF Protections
#CSRF_COOKIE_SECURE = True
#CSRF_USE_SESSIONS = False

# Delete Sessions
SESSION_COOKIE_SECURE=True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 24*3600

# Cross Site Scripting
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Re-direct non HTTPS requests to HTTPS
#SECURE_SSL_REDIRECT = True

# CSP Settings
CSP_SCRIPT_SRC = [
    "https://cdnjs.cloudflare.com",
    "https://cdn.jsdelivr.net",
    "https://code.jquery.com"
]

CSP_STYLE_SRC = ["https://code.cdn.mozilla.net"]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email settings
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']
                       
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_SSL = False    # use port 465
EMAIL_USE_TLS = True    # use port 587
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'