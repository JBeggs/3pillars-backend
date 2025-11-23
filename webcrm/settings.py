import sys
import os
from pathlib import Path
from datetime import datetime as dt
from django.utils.translation import gettext_lazy as _

from crm.settings import *          # NOQA
from common.settings import *       # NOQA
from tasks.settings import *        # NOQA
from voip.settings import *         # NOQA
from .datetime_settings import *    # NOQA

# ---- Django settings ---- #

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# To get new value of key use code:
# from django.core.management.utils import get_random_secret_key
# print(get_random_secret_key())
SECRET_KEY = os.environ.get('SECRET_KEY', 'j1c=6$s-dh#$ywt@(q4cm=j&0c*!0x!e-qm6k1%yoliec(15tn')

# Add your hosts to the list.
# Railway provides RAILWAY_PUBLIC_DOMAIN, but we'll use ALLOWED_HOSTS env var
# Also check RAILWAY_PUBLIC_DOMAIN for automatic Railway domain detection
allowed_hosts_str = os.environ.get('ALLOWED_HOSTS', '')
railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')

if allowed_hosts_str:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.101']

# Add Railway domain if available and not already in list
if railway_domain and railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(railway_domain)
    # Also add wildcard for Railway subdomains
    if '*.railway.app' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('*.railway.app')

# Database
# Railway automatically provides DATABASE_URL environment variable
import dj_database_url

# Choose database URL based on environment:
# - Deployed Railway containers: Use DATABASE_URL (internal, faster) - detected by PORT env var
# - Local railway run commands: Use DATABASE_PUBLIC_URL (public proxy works from local)
# - Local development: Use DATABASE_PUBLIC_URL if available, otherwise DATABASE_URL
# PORT is only set when actually running in Railway's container, not for railway run commands
is_railway_container = os.environ.get('PORT') is not None
if is_railway_container:
    # Actually deployed in Railway container - use internal DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    print("[DB Config] Railway container detected (PORT=%s), using internal DATABASE_URL" % os.environ.get('PORT'))
else:
    # Local development or railway run - ALWAYS prefer DATABASE_PUBLIC_URL
    # railway run commands can't resolve railway.internal hostnames
    database_url = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
    if os.environ.get('DATABASE_PUBLIC_URL'):
        print("[DB Config] Local/railway run detected, using DATABASE_PUBLIC_URL")
    else:
        print("[DB Config] No DATABASE_PUBLIC_URL, falling back to DATABASE_URL")

if database_url:
    # Parse the database URL directly using default parameter
    # This avoids relying on environment variable overrides
    db_config = dj_database_url.config(
        default=database_url,  # Pass URL directly
        conn_max_age=300,  # Reduced from 600 to recycle connections faster
        conn_health_checks=True,
    )
    
    # Ensure ENGINE is set correctly
    if 'ENGINE' not in db_config:
        db_config['ENGINE'] = 'django.db.backends.postgresql'
    
    # Add connection options for better reliability with Railway
    # psycopg2 connection parameters (these go in OPTIONS)
    db_config.setdefault('OPTIONS', {})
    db_config['OPTIONS'].update({
        'connect_timeout': 10,  # Connection timeout (seconds)
        'options': '-c statement_timeout=30000',  # 30 second query timeout
    })
    
    DATABASES = {
        'default': db_config
    }
else:
    # Local development - use SQLite
    DATABASES = {
        'default': {
            # for SQLite3
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'crm_db',

            # for MySQl (uncomment if needed)
            #'ENGINE': 'django.db.backends.mysql',
            #'PORT': '3306',

            # for PostgreSQL (uncomment if needed)
            # "ENGINE": "django.db.backends.postgresql",
            # 'PORT': '5432',

            'USER': 'crm_user',
            'PASSWORD': 'crmpass',
            'HOST': 'localhost',
        }
    }

EMAIL_HOST = '<specify host>'   # 'smtp.example.com'
EMAIL_HOST_PASSWORD = '<specify password>'
EMAIL_HOST_USER = 'crm@example.com'
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = 'CRM: '
EMAIL_USE_TLS = True

SERVER_EMAIL = 'test@example.com'
DEFAULT_FROM_EMAIL = 'test@example.com'

ADMINS = [("<Admin1>", "<admin1_box@example.com>")]   # specify admin

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

FORMS_URLFIELD_ASSUME_HTTPS = True

# Internationalization
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('ar', 'Arabic'),
    ('cs', 'Czech'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
    ('he', 'Hebrew'),
    ('hi', 'Hindi'),
    ('id', 'Indonesian'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    ('ko', 'Korean'),
    ('nl', 'Nederlands'),
    ('pl', 'Polish'),
    ('pt-br', 'Portuguese'),
    ('ro', 'Romanian'),
    ('ru', 'Russian'),
    ('tr', 'Turkish'),
    ('uk', 'Ukrainian'),
    ('vi', 'Vietnamese'),
    ('zh-hans', 'Chinese'),
]

TIME_ZONE = 'UTC'   # specify your time zone

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

LOGIN_URL = '/admin/login/'

# Application definition
INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # REST Framework
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    # CRM Apps
    'crm.apps.CrmConfig',
    'massmail.apps.MassmailConfig',
    'analytics.apps.AnalyticsConfig',
    'help',
    'tasks.apps.TasksConfig',
    'chat.apps.ChatConfig',
    'voip',
    'common.apps.CommonConfig',
    'settings',
    # API App
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
    'corsheaders.middleware.CorsMiddleware',  # CORS early, before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.utils.admin_redirect_middleware.AdminRedirectMiddleware',
    'common.utils.usermiddleware.UserMiddleware'
]

ROOT_URLCONF = 'webcrm.urls'

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

WSGI_APPLICATION = 'webcrm.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'
    }
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Changed for Railway/WhiteNoise

# WhiteNoise configuration for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

FIXTURE_DIRS = ['tests/fixtures']

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

SITE_ID = 1

SECURE_HSTS_SECONDS = 0  # set to 31536000 for the production server
# Set all the following to True for the production server
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_PRELOAD = False
X_FRAME_OPTIONS = "SAMEORIGIN"

# ---- CRM settings ---- #

# For more security, replace the url prefixes
# with your own unique value.
SECRET_CRM_PREFIX = '123/'
SECRET_ADMIN_PREFIX = '456-admin/'
SECRET_LOGIN_PREFIX = '789-login/'

# Specify ip of host to avoid importing emails sent by CRM
CRM_IP = "127.0.0.1"

CRM_REPLY_TO = ["'Do not reply' <crm@example.com>"]

# List of addresses to which users are not allowed to send mail.
NOT_ALLOWED_EMAILS = []

# List of applications on the main page and in the left sidebar.
APP_ON_INDEX_PAGE = [
    'tasks', 'crm', 'analytics',
    'massmail', 'common', 'settings'
]
MODEL_ON_INDEX_PAGE = {
    'tasks': {
        'app_model_list': ['Task', 'Memo']
    },
    'crm': {
        'app_model_list': [
            'Request', 'Deal', 'Lead', 'Company',
            'CrmEmail', 'Payment', 'Shipment'
        ]
    },
    'analytics': {
        'app_model_list': [
            'IncomeStat', 'RequestStat'
        ]
    },
    'massmail': {
        'app_model_list': [
            'MailingOut', 'EmlMessage'
        ]
    },
    'common': {
        'app_model_list': [
            'UserProfile', 'Reminder'
        ]
    },
    'settings': {
        'app_model_list': [
            'PublicEmailDomain', 'StopPhrase'
        ]
    }
}

# Country VAT value
VAT = 0    # %

# 2-Step Verification Credentials for Google Accounts.
#  OAuth 2.0
CLIENT_ID = ''
CLIENT_SECRET = ''
OAUTH2_DATA = {
    'smtp.gmail.com': {
        'scope': "https://mail.google.com/",
        'accounts_base_url': 'https://accounts.google.com',
        'auth_command': 'o/oauth2/auth',
        'token_command': 'o/oauth2/token',
    }
}
# Hardcoded dummy redirect URI for non-web apps.
REDIRECT_URI = ''

# Credentials for Google reCAPTCHA.
GOOGLE_RECAPTCHA_SITE_KEY = ''
GOOGLE_RECAPTCHA_SECRET_KEY = ''

GEOIP = False
GEOIP_PATH = MEDIA_ROOT / 'geodb'

# For user profile list
SHOW_USER_CURRENT_TIME_ZONE = False

NO_NAME_STR = _('Untitled')

# For automated getting currency exchange rate
LOAD_EXCHANGE_RATE = False
LOADING_EXCHANGE_RATE_TIME = "6:30"
LOAD_RATE_BACKEND = ""  # "crm.backends.<specify_backend>.<specify_class>"

# Ability to mark payments through a representation
MARK_PAYMENTS_THROUGH_REP = False

# Site headers
SITE_TITLE = 'CRM'
ADMIN_HEADER = "ADMIN"
ADMIN_TITLE = "CRM Admin"
INDEX_TITLE = _('Main Menu')

# Allow mailing
MAILING = True

# This is copyright information. Please don't change it!
COPYRIGHT_STRING = f"Django-CRM. Copyright (c) {dt.now().year}"
PROJECT_NAME = "Django-CRM"
PROJECT_SITE = "https://djangocrm.github.io/info/"


TESTING = sys.argv[1:2] == ['test']
if TESTING:
    SECURE_SSL_REDIRECT = False
    LANGUAGE_CODE = 'en'
    LANGUAGES = [('en', ''), ('uk', '')]

# ---- REST Framework Configuration ---- #

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Keep for admin
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings (for Flutter app)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Flutter web dev
    "http://127.0.0.1:3000",
    # Add your Flutter app domains when deployed
]

CORS_ALLOW_CREDENTIALS = True

# Optional: API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Django CRM API',
    'DESCRIPTION': 'REST API for Django CRM mobile app',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
