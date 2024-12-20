from django.core.management.base import BaseCommand
from django.db import transaction

from data import get_publisher_stats, publishers_ordered_by_title
from ui.models import Publisher


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        Publisher.objects.all().delete()
        for publisher_title, publisher_slug in publishers_ordered_by_title:
            stats_json = dict(get_publisher_stats(publisher_slug))
            publisher = Publisher(title=publisher_title, slug=publisher_slug, stats_json=stats_json)
            publisher.save()
