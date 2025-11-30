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


def file_types(stats_json):
    types = []
    if stats_json.get("activity_files"):
        types.append("iati-activities")
    if stats_json.get("organisation_files"):
        types.append("iati-organisations")
    if stats_json.get("activity_files") and stats_json.get("organisation_files"):
        types.append("both")
    return types


def import_reporting_org_metadata():
    keep_ids = []
    for reporting_org_dict in metadata_reporting_orgs["reporting_orgs"]:
        reporting_org, created = ReportingOrg.objects.get_or_create(id=reporting_org_dict["id"])
        keep_ids.append(reporting_org_dict["id"])
        reporting_org.human_readable_name = reporting_org_dict["human_readable_name"]
        reporting_org.short_name = reporting_org_dict["short_name"]
        reporting_org.metadata_json = reporting_org_dict
        reporting_org.save()
    for reporting_org in ReportingOrg.objects.all():
        if id not in keep_ids:
            reporting_org.delete()


def import_dataset_metadata():
    keep_ids = []
    for dataset_dict in metadata_datasets["datasets"]:
        dataset, created = Dataset.objects.get_or_create(id=dataset_dict["id"])
        keep_ids.append(dataset_dict["id"])
        dataset.reporting_org = ReportingOrg.objects.get(short_name=dataset_dict["reporting_org_short_name"])
        dataset.short_name = dataset_dict["short_name"]
        dataset.source_url = dataset_dict["source_url"]
        dataset.metadata_json = dataset_dict
        try:
            dataset.save()
        except ReportingOrg.DoesNotExist:
            print(f"ReportingOrg {dataset_dict["reporting_org_short_name"]} not found to link dataset to")
    for dataset in Dataset.objects.all():
        if id not in keep_ids:
            dataset.delete()

def import_stats():
    for reporting_org_dict in metadata_reporting_orgs["reporting_orgs"]:
        stats_json = dict(get_publisher_stats(reporting_org_dict["short_name"]))
        if not stats_json:
            stats_json = DEFAULT_STATS_JSON
        try:
            reporting_org = ReportingOrg.objects.get(id=reporting_org_dict["id"])
        except ReportingOrg.DoesNotExist:
            print(f"ReportingOrg {reporting_org_dict["id"]} ({reporting_org_dict["short_name"]}) not found")
            continue
        # reporting_org.stats_metadata_json = reporting_org_dict
        reporting_org.stats_json = stats_json
        reporting_org.has_future_transactions = timeliness.has_future_transactions(reporting_org_dict["short_name"])
        reporting_org.timeliness_frequency = timeliness.publisher_frequency_generate_row(reporting_org_dict["short_name"])
        reporting_org.forwardlooking = forwardlooking.generate_row(reporting_org_dict["short_name"])
        reporting_org.comprehensiveness = comprehensiveness.generate_row(reporting_org_dict["short_name"])
        reporting_org.validation_datasets = current_stats["inverted_file_publisher"].get(reporting_org_dict["short_name"], {}).get("validation", {}).get("fail", {})
        reporting_org.recipient_country_code = recipient_country_code(stats_json)
        reporting_org.file_types = file_types(stats_json)
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
        if not stats_json:
            stats_json = DEFAULT_STATS_JSON
        try:
            dataset = Dataset.objects.get(id=dataset_dict["id"])
        except Dataset.DoesNotExist:
            print(f"Dataset {dataset_dict["id"]} ({dataset_dict["short_name"]}) not found")
            continue
        dataset.stats_json = stats_json
        # dataset.stats_metadata_json = dataset_dict
        dataset.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            import_reporting_org_metadata()
            import_dataset_metadata()
        #with transaction.atomic():
        #    import_stats()
