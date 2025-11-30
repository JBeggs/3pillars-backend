import sys
import os
from pathlib import Path
from datetime import datetime as dt
from django.utils.translation import gettext_lazy as _

# Try to use pymysql as MySQLdb (for PythonAnywhere compatibility)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass  # mysqlclient or other MySQL driver will be used

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
# For PythonAnywhere, set ALLOWED_HOSTS environment variable or configure below
allowed_hosts_str = os.environ.get('ALLOWED_HOSTS', '')

if allowed_hosts_str:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]
else:
    # Default for local development
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.100']

# PythonAnywhere domains - automatically add based on username or default
pythonanywhere_username = os.environ.get('PYTHONANYWHERE_USERNAME', '')
if pythonanywhere_username:
    domain = f'{pythonanywhere_username}.pythonanywhere.com'
    if domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(domain)

# Always add 3pillars.pythonanywhere.com if not already present (for this deployment)
if '3pillars.pythonanywhere.com' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('3pillars.pythonanywhere.com')

# Database Configuration
# PythonAnywhere typically uses MySQL, but PostgreSQL and SQLite are also supported

# Check if we're on PythonAnywhere
ON_PYTHONANYWHERE = (
    'pythonanywhere.com' in os.environ.get('HTTP_HOST', '') or
    'pythonanywhere.com' in os.environ.get('SERVER_NAME', '') or
    bool(os.environ.get('PYTHONANYWHERE_USERNAME', ''))
)

if ON_PYTHONANYWHERE:   
    # PythonAnywhere MySQL configuration
    # Get credentials from environment variables or use defaults
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'yourusername$crm_db'),
            'USER': os.environ.get('DB_USER', os.environ.get('PYTHONANYWHERE_USERNAME', 'yourusername')),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'yourusername.mysql.pythonanywhere-services.com'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }
elif os.environ.get('DATABASE_URL'):
    # Support for DATABASE_URL (PostgreSQL, MySQL, etc.)
    import dj_database_url
    db_config = dj_database_url.config(
        conn_max_age=300,
        conn_health_checks=True,
    )
    DATABASES = {
        'default': db_config
    }
else:
    # Local development - use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'crm_db',
        }
    }

# Email Configuration
# Configure via environment variables or update directly
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')  # SMTP server hostname
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')  # SMTP username/email
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')  # SMTP password or app password
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))  # SMTP port (587 for TLS, 465 for SSL)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'  # Use TLS (True for port 587)
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'  # Use SSL (True for port 465)
EMAIL_SUBJECT_PREFIX = os.environ.get('EMAIL_SUBJECT_PREFIX', 'CRM: ')
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '10'))  # Timeout in seconds

# Email addresses
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@example.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)  # For error reports

# Reply-to address (optional) - can be string or list
CRM_REPLY_TO_STR = os.environ.get('CRM_REPLY_TO', '')
if CRM_REPLY_TO_STR:
    CRM_REPLY_TO = CRM_REPLY_TO_STR
else:
    CRM_REPLY_TO = DEFAULT_FROM_EMAIL

# Admin email addresses (for error reports)
# Format: [("Name", "email@example.com"), ...]
ADMINS_STR = os.environ.get('ADMINS', '')
if ADMINS_STR:
    # Parse from environment: "Name1:email1@example.com,Name2:email2@example.com"
    ADMINS = []
    for admin_str in ADMINS_STR.split(','):
        if ':' in admin_str:
            name, email = admin_str.split(':', 1)
            ADMINS.append((name.strip(), email.strip()))
        else:
            # Just email, use email as name
            ADMINS.append((admin_str.strip(), admin_str.strip()))
else:
    ADMINS = [("Admin", DEFAULT_FROM_EMAIL)]  # Default to DEFAULT_FROM_EMAIL

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
    # E-commerce Multi-Tenant App
    'ecommerce.apps.EcommerceConfig',
    # FCM (Firebase Cloud Messaging)
    'fcm.apps.FcmConfig',
    # News Platform App
    'news.apps.NewsConfig',
]

# WhiteNoise middleware (only for non-PythonAnywhere deployments)
WHITENOISE_MIDDLEWARE = []
if not ON_PYTHONANYWHERE:
    try:
        import whitenoise
        WHITENOISE_MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware']
    except ImportError:
        # WhiteNoise not installed - skip it (for local dev without whitenoise)
        pass

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    *WHITENOISE_MIDDLEWARE,
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
STATIC_URL = '/static/'

# Static files directories (where Django looks for static files)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
] if (BASE_DIR / 'static').exists() else []

if ON_PYTHONANYWHERE:
    # PythonAnywhere serves static files from /static/ URL
    STATIC_ROOT = Path.home() / 'static' / 'static'
else:
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
if ON_PYTHONANYWHERE:
    # PythonAnywhere serves media files from /media/ URL
    MEDIA_ROOT = Path.home() / 'media'
else:
    MEDIA_ROOT = BASE_DIR / 'media'

# Ensure media directory exists
if not MEDIA_ROOT.exists():
    try:
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass  # Directory creation may fail in some environments

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

# CRM_REPLY_TO is set above from environment variable or DEFAULT_FROM_EMAIL
# If you need a list format, override it here or set CRM_REPLY_TO in .env

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
COPYRIGHT_STRING = f"Three Pillars Backend. Copyright (c) {dt.now().year}"
PROJECT_NAME = "Three Pillars Backend"
PROJECT_SITE = "https://github.com/JBeggs/3pillars-backend"


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

# CORS Settings (for React frontend and Flutter app)
CORS_ALLOWED_ORIGINS = [
    # React frontend (3piller)
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.1.100:3000",  # Local network access
    # Flutter web dev
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    # Add your production domains when deployed
]

# Allow all origins for development (set to False in production)
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'

CORS_ALLOW_CREDENTIALS = True

# CORS headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-company-id',  # For multi-tenant API
]

# Firebase Configuration
# Allow override via environment variable (useful for PythonAnywhere)
# If not set, defaults to project root
FIREBASE_CREDENTIALS_PATH = os.environ.get(
    'FIREBASE_CREDENTIALS_PATH',
    os.path.join(BASE_DIR, 'firebase-service-account.json')
)
# Check if file exists, log warning if not (won't crash app)
if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(
        f"Firebase credentials file not found at: {FIREBASE_CREDENTIALS_PATH}. "
        f"FCM functionality will be disabled. "
        f"Set FIREBASE_CREDENTIALS_PATH environment variable or upload the file."
    )

# Optional: API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Django CRM API',
    'DESCRIPTION': 'REST API for Django CRM mobile app',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
