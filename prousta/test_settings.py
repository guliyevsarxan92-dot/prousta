"""Offline test configuration. Never uses the workspace's database or storage."""
import os

os.environ['SECRET_KEY'] = 'isolated-tests-only-' + 'x' * 64
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['DEBUG'] = 'True'

from .settings import *  # noqa: F403,E402

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1', 'prousta.az']
STORAGES = {
    'receipts': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Optional local-only PostgreSQL integration database. Never accepts a remote host.
if os.getenv('TEST_DATABASE_URL'):
    import dj_database_url
    _test_database = dj_database_url.parse(os.environ['TEST_DATABASE_URL'])
    if not (_test_database['HOST'].startswith('/tmp/prousta-isolated-pg-')
            and _test_database['NAME'] == 'postgres'):
        raise RuntimeError('TEST_DATABASE_URL must point to the isolated /tmp PostgreSQL cluster.')
    DATABASES = {'default': _test_database}
