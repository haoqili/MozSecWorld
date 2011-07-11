# Django settings file for a project based on the playdoh template.
# settings_local.py (for private settings) will append to 
# this file by doing "from settings import *"
# and manage.py will just load settings_local.py

import os
import socket

from django.utils.functional import lazy

# Make file paths relative to settings.
ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

ROOT_PACKAGE = os.path.basename(ROOT)

# Is this a dev instance?
DEV = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

# DATABASES values set in settings_local.py

# Recipients of traceback emails and other notifications.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# Debugging displays nice error messages, but leaks memory. Set this to False
# on all server instances and True only for development.
DEBUG = TEMPLATE_DEBUG = True

# Is this a development instance? Set this to True on development/master
# instances and False on stage/prod.
DEV = True


# Site ID is used by Django's Sites framework.
SITE_ID = 1


## Internationalization.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Gettext text domain
TEXT_DOMAIN = 'messages'
STANDALONE_DOMAINS = [TEXT_DOMAIN, 'javascript']
TOWER_KEYWORDS = {'_lazy': None}

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

## Accepted locales

# On dev instances, the list of accepted locales defaults to the contents of 
# the `locale` directory.  A localizer can add their locale in the l10n 
# repository (copy of which is checked out into `locale`) in order to start 
# testing the localization on the dev server.
try:
    DEV_LANGUAGES = [
        loc.replace('_', '-') for loc in os.listdir(path('locale'))
        if os.path.isdir(path('locale', loc)) and loc != 'templates'
    ]
except OSError:
    DEV_LANGUAGES = ('en-US',)

# On stage/prod, the list of accepted locales is manually maintained.  Only 
# locales whose localizers have signed off on their work should be listed here.
PROD_LANGUAGES = (
    'en-US',
)

def lazy_lang_url_map():
    from django.conf import settings
    langs = DEV_LANGUAGES if settings.DEV else PROD_LANGUAGES
    return dict([(i.lower(), i) for i in langs])

LANGUAGE_URL_MAP = lazy(lazy_lang_url_map, dict)()

# Override Django's built-in with our native names
def lazy_langs():
    from django.conf import settings
    from product_details import product_details
    langs = DEV_LANGUAGES if settings.DEV else PROD_LANGUAGES
    return dict([(lang.lower(), product_details.languages[lang]['native'])
                 for lang in langs])

# Where to store product details etc.
PROD_DETAILS_DIR = path('lib/product_details_json')

LANGUAGES = lazy(lazy_langs, dict)()

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = ['media']


HOSTNAME = socket.gethostname()
DOMAIN = HOSTNAME
# Full base URL for your main site including protocol.  No trailing slash.
#   Example: https://addons.mozilla.org
SITE_URL = 'http://%s' % DOMAIN
STATIC_URL = SITE_URL

## Media and templates.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1iz#v0m55@h26^m6hxk3a7at*h$qj_2a$juu1#nv50548j(x1v'

# List of callables that know how to import templates from various sources.
# Template_loaders find templates in the app
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages',

    'commons.context_processors.i18n',
    'jingo_minify.helpers.build_ids',
    
    'msw.context_processors.global_settings',
)

TEMPLATE_DIRS = (
    path('templates'),
    # change it to your own path
    #"/Users/haoqili/dev/playdoh/playdoh/playdoh/templates",
)

def JINJA_CONFIG():
    import jinja2
    from django.conf import settings
#    from caching.base import cache
    config = {'extensions': ['tower.template.i18n', 'jinja2.ext.do',
                             'jinja2.ext.with_', 'jinja2.ext.loopcontrols'],
              'finalize': lambda x: x if x is not None else ''}
#    if 'memcached' in cache.scheme and not settings.DEBUG:
        # We're passing the _cache object directly to jinja because
        # Django can't store binary directly; it enforces unicode on it.
        # Details: http://jinja.pocoo.org/2/documentation/api#bytecode-cache
        # and in the errors you get when you try it the other way.
#        bc = jinja2.MemcachedBytecodeCache(cache._cache,
#                                           "%sj2:" % settings.CACHE_PREFIX)
#        config['cache_size'] = -1 # Never clear the cache
#        config['bytecode_cache'] = bc
    return config

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'main_css': (
            'css/msw/main.css',
        ),
        'example_css': (
            'css/examples/main.css',
        ),
    },
    'js': {
        # JS files common to the entire msw site.
        'common': (
            'js/libs/jquery-1.6.2.min.js',
        ),
        'xframe_checkurl': (
            'js/msw/xframe_checkurl.js',
        ),
        'httponly_viewcookie': (
            'js/msw/httponly_viewcookie.js',
        ),
        'sql_ajax': (
            'js/msw/sql_ajax.js',
        ),
        'sql_button': (
            'js/msw/sql_button.js',
        ),
        'richtext_safeurl': (
            'js/msw/richtext_safeurl.js',
        ),
        'csp_alert': (
            'js/msw/csp_external.js',
        ),
        'captcha_return': (
            'js/msw/captcha_return.js',
        ),
        'google_recState': (
            'js/google/recState.js',
        ),
        'google_recaptcha': (
            'js/google/recaptcha.js',
        ),
        'moz_recaptcha': (
            'js/msw/moz_recaptcha.js',
        )
    }
}


## Middlewares, apps, URL configs.

MIDDLEWARE_CLASSES = (
    'commons.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # authenticationmiddleware must be after sessionmiddleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'commonware.middleware.FrameOptionsHeader',

    # content security policy: 
    # https://github.com/mozilla/django-csp
    'csp.middleware.CSPMiddleware',
)


ROOT_URLCONF = '%s.urls' % ROOT_PACKAGE

INSTALLED_APPS = (
    'msw', # MozSecWorld! :D
    # Local apps
    'commons',  # Content common to most playdoh-based apps.
    'jingo_minify',
    'tower',  # for ./manage.py extract (L10n)

    'examples',  # Example code. Can (and should) be removed for actual projects.

    # We need this so the jsi18n view will pick up our locale directory.
    ROOT_PACKAGE,

    # Third-party apps
    'commonware.response.cookies',
    'djcelery',
    'django_nose',

    # Django contrib apps
    'django.contrib.auth',
    'django_sha2',  # Load after auth to monkey-patch it.

    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # L10n
    'product_details',

    # Content security policy
    'csp',
)

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('apps/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
    ],

    ## Use this if you have localizable HTML files:
    #'lhtml': [
    #    ('**/templates/**.lhtml',
    #        'tower.management.commands.extract.extract_tower_template'),
    #],

    ## Use this if you have localizable JS files:
    #'javascript': [
        # Make sure that this won't pull in strings from external libraries you
        # may use.
    #    ('media/js/**.js', 'javascript'),
    #],
}

# Path to Java. Used for compress_assets.
JAVA_BIN = '/usr/bin/java'

## Auth
PWD_ALGORITHM = 'bcrypt'
BCRYPT_ROUNDS = 12 # 12 is the default
# HMAC_KEYS set in settings_local.py

## Tests
TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

## Celery
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'playdoh'
BROKER_PASSWORD = 'playdoh'
BROKER_VHOST = 'playdoh'
BROKER_CONNECTION_TIMEOUT = 0.1
CELERY_RESULT_BACKEND = 'amqp'
CELERY_IGNORE_RESULT = True

## My own stuff
GOOGLE_SAFEBROWSING_LOOKUP = True
GSB_HOST = "https://sb-ssl.google.com"
GSB_PATH = "/safebrowsing/api/lookup"
# GSB_API_KEY set in settings_local.py

## Accounts stuff
AUTH_PROFILE_MODULE = 'msw.UserProfile'

## Sessions 
# copied from zamboni https://github.com/jbalogh/zamboni/blob/master/settings.py
#SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1209600
# TODO: When we use SSL, enable SESSION_COOKIE_SECURE!
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
# incorrect SESSION_COOKIE_DOMAIN also causes browser doesn't ... have cookies enabled
# hostname is "host-3-248.mv.mozilla.com", so can't use
#SESSION_COOKIE_DOMAIN = ".%s" % DOMAIN 

# https://docs.djangoproject.com/en/dev/ref/settings/?from=olddocs#login-url

# The URL where requests are redirected for login, especially when using the login_required() decorator.
# Default: '/accounts/login/'
LOGIN_URL = '/msw/templates'

# The URL where requests are redirected after login when the contrib.auth.login view gets no next parameter.
# Default: '/accounts/profile/'
LOGIN_REDIRECT_URL = "/msw/"

# Recaptcha stuff http://curioushq.blogspot.com/2011/07/recaptcha-on-django.html
# create keys https://www.google.com/recaptcha/admin/create
# RECAPTCHA_PUBLIC_KEY set in settings_local.py
# RECAPTCHA_PRIVATE_KEY set in settings_local.py
# RECAPTCHA_URL set in settings_local.py


# CSP Settings
# based on zamboni
#CSP_REPORT_URI = '/services/csp/repoyt'
CSP_REPORT_URI = 'http://10.250.7.136:8010'
#CSP_POLICY_URI = '/services/csp/policy?build=%s' % build_id
#CSP_REPORT_ONLY = True 

CSP_ALLOW = ("'self'",
            "https://api-secure.recaptcha.net", 
            "https://www.google.com", 
            "http://www.google.com", 
            "http://haoqili.scripts.mit.edu",
               "https://fpdownload.macromedia.com",
               "http://www.adobe.com",
        
            )
CSP_IMG_SRC = ("'self'", STATIC_URL,
            "https://api-secure.recaptcha.net", 
               "https://www.google.com",  # Recaptcha comes from google
               "http://www.google.com",  # Recaptcha comes from google
               "http://haoqili.scripts.mit.edu",
               "https://fpdownload.macromedia.com",
               "http://www.adobe.com",
                # WHAT IS THE CSP TO MAKE CAPTACH WORK?
                "https://static-cdn.addons.mozilla.net",
                "https://statse.webtrendslive.com", 
                "https://www.getpersonas.com"
              )    
CSP_SCRIPT_SRC = ("'self'", STATIC_URL,
            "https://api-secure.recaptcha.net", 
                  "https://www.google.com",  # Recaptcha
                  "http://www.google.com",  # Recaptcha
               "http://haoqili.scripts.mit.edu",
               "https://fpdownload.macromedia.com",
               "http://www.adobe.com",
                "https://static-cdn.addons.mozilla.net",
                "https://www.paypalobjects.com",
                  )    
CSP_STYLE_SRC = ("'self'", STATIC_URL,"https://static-cdn.addons.mozilla.net")
CSP_OBJECT_SRC = ("'none'",)
CSP_MEDIA_SRC = ("'none'",)
CSP_FRAME_SRC = ("*", # allow all for the x-frame-options demo
               "https://www.google.com",  # Recaptcha comes from google
               "http://www.google.com",  # Recaptcha comes from google
                "https://s3.amazonaws.com", 
                "https://getsatisfaction.com",
                )    
CSP_FONT_SRC = ("'self'", "fonts.mozilla.com", "www.mozilla.com", )
# self is needed for paypal which sends x-frame-options:allow when needed.
# x-frame-options:DENY is sent the rest of the time.
CSP_FRAME_ANCESTORS = ("'self'",)
