import os

DEBUG = False
LANGUAGE_CODE = os.environ['QQQ_LANGUAGE']
if os.environ.has_key('QQQ_DEBUG'):
    DEBUG = True

# remember to change the default record in db table django_site!
SITE_ID = 1

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_DIRS = (os.path.join(PROJECT_DIR, 'templates'))
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'files')
EMAIL_HOST = 'localhost'
EMAIL_PORT = '25'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
MEDIA_URL = '/files/'
TEMPLATE_DEBUG = DEBUG
ADMINS = (('jj', 'jj@qualityquizquestions.org'))
MANAGERS = ADMINS
AUTH_PROFILE_MODULE = "user_profile.Profile"
ROOT_URLCONF = 'urls'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_ACTIVATION_DAYS = 7
DEFAULT_FROM_EMAIL = "Quality Quiz Questions <support@qualityquizquestions.org>"
TIME_ZONE = 'GB'
USE_I18N = True
USE_L10N = True
SECRET_KEY = [REDACTED]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'qualityquizquestions_' + LANGUAGE_CODE,
        'USER': 'django',
        'PASSWORD': [REDACTED],
        # you can leave the following blank, but you'd have to disable ident authentication in
        # /etc/postgresql/.../pg_hba.conf
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
#    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)

INSTALLED_APPS = (
#    'localeurl',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
#    'django.contrib.messages',
    'django.contrib.markup',
    'qqq',
    'qqq.questions',
    'qqq.revisions',
    'qqq.collections',
    'qqq.posts',
    'debate',
    'messages',
    'user_profile',
    'tagging',
    'voting',
    'registration',
    'django_extensions',
#    'debug_toolbar',
)
