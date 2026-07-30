from django.core.management.base import BaseCommand

from ... import comprehensiveness, filepaths, forwardlooking, humanitarian, summary_stats, timeliness
from ...data import (
    JSONDir,
    current_stats,
    get_publisher_stats,
    metadata_datasets,
    metadata_reporting_orgs,
)
from ...models import Dataset, ReportingOrg


def recipient_country_code(stats_json):
    try:
        activity_level = stats_json.get("codelist_values", {}).get(".//recipient-country/@code", {}).keys()
        transaction_level = (
            stats_json.get("codelist_values", {}).get(".//transaction/recipient-country/@code", {}).keys()
        )
        return sorted(list(activity_level | transaction_level))
    except AttributeError:
        return []


def file_types(stats_json):
    types = []
    if stats_json.get("activity_files"):
        types.append("iati-activities")
    if stats_json.get("organisation_files"):
        types.append("iati-organisations")
    if stats_json.get("activity_files") and stats_json.get("organisation_files"):
        types.append("both")
    return types


class Command(BaseCommand):
    def handle(self, *args, **options):
        for reporting_org_dict in metadata_reporting_orgs["reporting_orgs"]:
            stats_json = dict(get_publisher_stats(reporting_org_dict["short_name"]))
            if not stats_json:
                continue
            try:
                # assumes metadata import has been run first
                reporting_org = ReportingOrg.objects.get(
                    id=reporting_org_dict["id"],
                )
            except ReportingOrg.DoesNotExist:
                print(f"Reporting Org {reporting_org_dict["id"]} ({reporting_org_dict["short_name"]}), not found")
                continue
            reporting_org.stats_json = stats_json
            reporting_org.has_future_transactions = timeliness.has_future_transactions(
                reporting_org_dict["short_name"]
            )
            reporting_org.timeliness_frequency = timeliness.publisher_frequency_generate_row(
                reporting_org_dict["short_name"]
            )
            reporting_org.forwardlooking = forwardlooking.generate_row(reporting_org_dict["short_name"])
            reporting_org.comprehensiveness = comprehensiveness.generate_row(reporting_org_dict["short_name"])
            reporting_org.validation_datasets = (
                current_stats["inverted_file_publisher"]
                .get(reporting_org_dict["short_name"], {})
                .get("validation", {})
                .get("fail", {})
            )
            reporting_org.recipient_country_code = recipient_country_code(stats_json)
            reporting_org.file_types = file_types(stats_json)
            reporting_org.save()
            reporting_org.humanitarian = humanitarian.generate_row(reporting_org)
            reporting_org.summary_stats = summary_stats.generate_row(reporting_org)
            reporting_org.save()

        dataset_short_names = set()
        for dataset_dict in metadata_datasets["datasets"]:
            if dataset_dict["short_name"] in dataset_short_names:
                print(f"ERROR: duplicate Dataset short_name: {dataset_dict["short_name"]}")
                continue
            dataset_short_names.add(dataset_dict["short_name"])
            stats_json = dict(
                JSONDir(
                    filepaths.join_stats_path(
                        f"current/aggregated-file/{dataset_dict["reporting_org_short_name"]}/{dataset_dict["short_name"]}"
                    )
                )
            )
            if not stats_json:
                continue
            try:
                # assumes metadata import has been run first
                dataset = Dataset.objects.get(
                    id=dataset_dict["id"],
                )
            except Dataset.DoesNotExist:
                print(f"Dataset {dataset_dict["id"]} ({dataset_dict["short_name"]}), not found")
                continue
            dataset.stats_json = stats_json
            dataset.save()
