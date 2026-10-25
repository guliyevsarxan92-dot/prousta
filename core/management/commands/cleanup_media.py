from django.core.management.base import BaseCommand
from core.models import MediaCleanupTask
from core.media_cleanup import process_task


class Command(BaseCommand):
    help = 'Retry committed media cleanup tasks. Run periodically; never deletes referenced files.'

    def handle(self, *args, **options):
        ids = list(MediaCleanupTask.objects.order_by('created_at').values_list('pk', flat=True)[:100])
        for pk in ids:
            process_task(pk)
        self.stdout.write(f'Processed: {len(ids)}; remaining: {MediaCleanupTask.objects.count()}')
