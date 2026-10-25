"""Static asset compilation only; do not use as runtime settings."""
from .test_settings import *  # noqa: F403

STORAGES['staticfiles'] = {  # noqa: F405
    'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
}
