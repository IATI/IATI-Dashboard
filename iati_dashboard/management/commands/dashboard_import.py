from django.core.management.base import BaseCommand
from django.db import transaction

from ... import comprehensiveness, forwardlooking, humanitarian, summary_stats, timeliness
from ...data import get_publisher_stats, publishers_ordered_by_title
from ...models import Publisher


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        Publisher.objects.all().delete()
        for publisher_title, publisher_slug in publishers_ordered_by_title:
            stats_json = dict(get_publisher_stats(publisher_slug))
            publisher = Publisher(
                title=publisher_title,
                slug=publisher_slug,
                stats_json=stats_json,
                has_future_transactions=timeliness.has_future_transactions(publisher_slug),
                timeliness_frequency=timeliness.publisher_frequency_generate_row(publisher_slug),
                forwardlooking=forwardlooking.generate_row(publisher_slug),
                comprehensiveness=comprehensiveness.generate_row(publisher_slug),
                humanitarian=humanitarian.generate_row(publisher_slug),
            )
            publisher.summary_stats = (summary_stats.generate_row(publisher),)
            publisher.save()
