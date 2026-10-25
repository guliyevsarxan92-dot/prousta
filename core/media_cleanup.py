import logging

from django.core.files.storage import storages
from django.conf import settings
from django.db import transaction
from django.db.models import F

from .models import ElanShekil, MediaCleanupTask, Odenis, Profil

logger = logging.getLogger('core')


@transaction.atomic
def process_task(pk):
    task = MediaCleanupTask.objects.select_for_update().filter(pk=pk).first()
    if task is None:
        return
    if task.storage_alias == 'receipts':
        referenced = Odenis.objects.filter(qebz=task.name).exists()
    else:
        referenced = (ElanShekil.objects.filter(shekil=task.name).exists()
                      or Profil.objects.filter(avatar=task.name).exists())
    if not referenced:
        try:
            storages[task.storage_alias].delete(task.name)
        except Exception as exc:
            MediaCleanupTask.objects.filter(pk=pk).update(attempts=F('attempts') + 1,
                                                         last_error=type(exc).__name__[:100])
            logger.error('Media cleanup failed; queued for retry: task=%s', pk)
            return
    task.delete()


def enqueue(name, alias='default'):
    task = MediaCleanupTask.objects.create(name=name, storage_alias=alias)
    if settings.MEDIA_CLEANUP_EAGER:
        transaction.on_commit(lambda: process_task(task.pk))
