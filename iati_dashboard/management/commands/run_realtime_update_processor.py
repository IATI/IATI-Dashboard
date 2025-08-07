from django.conf import settings
from django.core.management.base import BaseCommand

from ...registry_event_processor.registry_event_processor import RegistryEventProcessor


class Command(BaseCommand):
    def handle(self, *args, **options):
        registry_processor = RegistryEventProcessor(args=settings.REGISTRY_UPDATE_PROCESSOR)
        registry_processor.run()
