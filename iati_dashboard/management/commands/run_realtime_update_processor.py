from django.conf import settings
from django.core.management.base import BaseCommand

from ...registry_event_processor.registry_event_processor import MessageProcessor


class Command(BaseCommand):
    def handle(self, *args, **options):
        message_processor = MessageProcessor(args=settings.REALTIME_UPDATE_PROCESSOR)
        message_processor.run()
