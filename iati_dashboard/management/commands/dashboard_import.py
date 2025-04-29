from django.core.management.base import BaseCommand
from django.db import transaction

from ... import comprehensiveness, filepaths, forwardlooking, humanitarian, summary_stats, timeliness
from ...data import JSONDir, ckan, current_stats, get_publisher_stats, publishers_ordered_by_title
from ...models import Dataset, Publisher


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        Publisher.objects.all().delete()
        Dataset.objects.all().delete()

        for publisher_title, publisher_slug in publishers_ordered_by_title:
            stats_json = dict(get_publisher_stats(publisher_slug))
            publisher = Publisher(
                human_readable_name=publisher_title,
                short_name=publisher_slug,
                stats_json=stats_json,
                has_future_transactions=timeliness.has_future_transactions(publisher_slug),
                timeliness_frequency=timeliness.publisher_frequency_generate_row(publisher_slug),
                forwardlooking=forwardlooking.generate_row(publisher_slug),
                comprehensiveness=comprehensiveness.generate_row(publisher_slug),
                humanitarian=humanitarian.generate_row(publisher_slug),
                validation_datasets=current_stats["inverted_file_publisher"][publisher_slug]["validation"].get(
                    "fail", {}
                ),
            )
            publisher.summary_stats = summary_stats.generate_row(publisher)
            publisher.save()

        for publisher_short_name, datasets_dict in ckan.items():
            for dataset_short_name, dataset_dict in datasets_dict.items():
                print(dataset_short_name)
                stats_json = dict(
                    JSONDir(
                        filepaths.join_stats_path(
                            f"current/aggregated-file/{publisher_short_name}/{dataset_short_name}"
                        )
                    )
                )
                try:
                    dataset = Dataset(
                        publisher=Publisher.objects.get(short_name=publisher_short_name),
                        short_name=dataset_short_name,
                        source_url=dataset_dict["resource"]["url"],
                        stats_json=stats_json,
                    )
                    dataset.save()
                except Publisher.DoesNotExist:
                    print("Publisher", publisher_short_name, "not found")
