"""
Django settings for johnslist project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# import secret key and email password settings
try:
    from secret_settings import *
except:
    print ' => ERROR: copy secret_settings.py.template to secret_settings.py and set the variables inside'
    exit(1)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

PROJECT_NAME="BoilerConnect"

# SECURITY WARNING: keep the secret key used in production secret!
# NOTE: set variable in secret_settings.py
# SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'easy_thumbnails',
    'guardian',
    'notifications',
    'widget_tweaks',
    'sniplates',
    'rangefilter',
    'import_export',
    'password_reset'
)

try:
    import django_extensions
    INSTALLED_APPS += ('django_extensions',)
except ImportError:
    pass

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default
    'guardian.backends.ObjectPermissionBackend',
)

ROOT_URLCONF = 'johnslist.urls'

WSGI_APPLICATION = 'johnslist.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
            # list if you haven't customized them:
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.request',
            'main.context_processors.global_settings',
        ],
    },
}]

if DEBUG:
    try:
        import debug_toolbar
        INTERNAL_IPS = ('127.0.0.1',)
        MIDDLEWARE_CLASSES += (
            'debug_toolbar.middleware.DebugToolbarMiddleware',
        )

        INSTALLED_APPS += (
            'debug_toolbar',
        )

        DEBUG_TOOLBAR_PANELS = [
            'debug_toolbar.panels.versions.VersionsPanel',
            'debug_toolbar.panels.timer.TimerPanel',
            'debug_toolbar.panels.settings.SettingsPanel',
            'debug_toolbar.panels.headers.HeadersPanel',
            'debug_toolbar.panels.request.RequestPanel',
            'debug_toolbar.panels.sql.SQLPanel',
            'debug_toolbar.panels.staticfiles.StaticFilesPanel',
            'debug_toolbar.panels.templates.TemplatesPanel',
            'debug_toolbar.panels.cache.CachePanel',
            'debug_toolbar.panels.signals.SignalsPanel',
            'debug_toolbar.panels.logging.LoggingPanel',
            'debug_toolbar.panels.redirects.RedirectsPanel',
        ]

        ## enable graphing via
        ## python manage.py graph_models -a > proj.dot
        ## python manage.py graph_models -a -g -o models.png
        GRAPH_MODELS = {
            'all_applications': True,
            'group_models': True,
        }
    except ImportError:
        pass

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = '../media'
MEDIA_URL = '/media/'

PIC_POPULATE_DIR = '../population_pics/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/srv/www/epics/static/'

# django auth settings
# where to redirect if login is required
LOGIN_URL = '/login'
# where to redirect after login if there was no last page ('next' variable)
LOGIN_REDIRECT_URL = '/'

# custom defined settings

# notifications extra fields
NOTIFICATIONS_USE_JSONFIELD = True

# generic redirect url
REDIRECT_URL = '/'

# django guardian config
ANONYMOUS_USER_ID = -1

# email configuration
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'boilerconnect1@gmail.com'
# NOTE: set variable in secret_settings.py
# EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
