LOCAL_SETTINGS = True
from base.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DATABASES.update({
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'opencmdb',                      # Or path to database file if using sqlite3.
        'USER': 'opencmdb',                     # Not used with sqlite3.
        'PASSWORD': 'opencmdb',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS':{'charset': 'utf8', }
    },
})
