from django.core.management.base import BaseCommand
from django.db import transaction

from ... import comprehensiveness, filepaths, forwardlooking, humanitarian, summary_stats, timeliness
from ...data import (
    JSONDir,
    current_stats,
    get_publisher_stats,
    metadata_datasets,
    metadata_reporting_orgs,
)
from ...models import DEFAULT_STATS_JSON, Dataset, ReportingOrg


def recipient_country_code(stats_json):
    try:
        activity_level = stats_json.get("codelist_values", {}).get(".//recipient-country/@code", {}).keys()
        transaction_level = (
            stats_json.get("codelist_values", {}).get(".//transaction/recipient-country/@code", {}).keys()
        )
        return sorted(list(activity_level | transaction_level))
    except AttributeError:
        return []


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        ReportingOrg.objects.all().delete()
        Dataset.objects.all().delete()

        for reporting_org_dict in metadata_reporting_orgs["reporting_orgs"]:
            stats_json = dict(get_publisher_stats(reporting_org_dict["short_name"]))
            if not stats_json:
                stats_json = DEFAULT_STATS_JSON
            reporting_org = ReportingOrg(
                id=reporting_org_dict["id"],
                human_readable_name=reporting_org_dict["human_readable_name"],
                short_name=reporting_org_dict["short_name"],
                metadata_json=reporting_org_dict,
                stats_json=stats_json,
                has_future_transactions=timeliness.has_future_transactions(reporting_org_dict["short_name"]),
                timeliness_frequency=timeliness.publisher_frequency_generate_row(reporting_org_dict["short_name"]),
                forwardlooking=forwardlooking.generate_row(reporting_org_dict["short_name"]),
                comprehensiveness=comprehensiveness.generate_row(reporting_org_dict["short_name"]),
                validation_datasets=current_stats["inverted_file_publisher"]
                .get(reporting_org_dict["short_name"], {})
                .get("validation", {})
                .get("fail", {}),
                recipient_country_code=recipient_country_code(stats_json),
            )
            reporting_org.save()
            reporting_org.humanitarian = humanitarian.generate_row(reporting_org)
            reporting_org.summary_stats = summary_stats.generate_row(reporting_org)
            reporting_org.save()

        for dataset_dict in metadata_datasets["datasets"]:
            stats_json = dict(
                JSONDir(
                    filepaths.join_stats_path(
                        f"current/aggregated-file/{dataset_dict["reporting_org_short_name"]}/{dataset_dict["short_name"]}"
                    )
                )
            )
            try:
                dataset = Dataset(
                    id=dataset_dict["id"],
                    reporting_org=ReportingOrg.objects.get(short_name=dataset_dict["reporting_org_short_name"]),
                    short_name=dataset_dict["short_name"],
                    source_url=dataset_dict["source_url"],
                    stats_json=stats_json,
                    metadata_json=dataset_dict,
                )
                dataset.save()
            except ReportingOrg.DoesNotExist:
                print("Publisher", dataset_dict["reporting_org_short_name"], "not found")
