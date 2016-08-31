from distutils.version import LooseVersion
from django import VERSION as DJ_VER
from cms import __version__ as CMS_VER

SITE_ID = 1
SECRET_KEY = 'fake-key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

ROOT_URLCONF = 'test_urls'

if DJ_VER >= (1, 8):
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['djangocms_ical/tests'],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'sekizai.context_processors.sekizai'
                ],
            },
        },
    ]
else:
    TEMPLATE_DIRS = ['djangocms_ical/tests']
    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.core.context_processors.request',
        'sekizai.context_processors.sekizai',
    )


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

tree = 'treebeard'

if LooseVersion(CMS_VER) < LooseVersion('3.1'):
    tree = 'mptt'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'djangocms_ical',
    'cms',
    'menus',
    tree,
    'sekizai',
)

LANGUAGE_CODE = 'en'
LANGUAGES = (('en', 'English'),)

CMS_TEMPLATES = (('bogus.html', 'Bogus'),)
