from .base import *

DEBUG = True

# For development, we might want to allow all hosts
ALLOWED_HOSTS = ['*']

# You can override other settings here specifically for development
# For example, using a local SQLite if you don't want to use Postgres yet
# DATABASES['default'] = {
#     'ENGINE': 'django.db.backends.sqlite3',
#     'NAME': BASE_DIR / 'db.sqlite3',
# }

# Static files for development
INSTALLED_APPS += ['debug_toolbar'] if env.bool('USE_DEBUG_TOOLBAR', default=False) else []
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware'] if env.bool('USE_DEBUG_TOOLBAR', default=False) else []
