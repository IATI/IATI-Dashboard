import datetime
import json
import os
import uuid

from django.core.management.base import BaseCommand
from django.db import transaction

from ... import filepaths
from ...models import Dataset, ReportingOrg


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("metadata_path", nargs="?")

    @transaction.atomic
    def handle(self, *args, metadata_path=None, **options):
        if not metadata_path:
            metadata_path = filepaths.join_stats_path("current/bulk-data-service-metadata")
        with open(os.path.join(metadata_path, "reporting-orgs.json")) as fp:
            metadata_reporting_orgs = json.load(fp)
        with open(os.path.join(metadata_path, "datasets-full.json")) as fp:
            metadata_datasets = json.load(fp)

        reporting_org_ids_before = set(ReportingOrg.objects.values_list("id", flat=True))
        reporting_org_ids_after = set()

        for reporting_org_dict in metadata_reporting_orgs["reporting_orgs"]:
            try:
                dup_reporting_org = ReportingOrg.objects.get(short_name=reporting_org_dict["short_name"])
            except ReportingOrg.DoesNotExist:
                pass
            else:
                if dup_reporting_org.id != uuid.UUID(reporting_org_dict["id"]):
                    reporting_org_ids_before.remove(dup_reporting_org.id)
                    dup_reporting_org.delete()
                    print(f"ERROR: duplicate reporting_org short_name: {reporting_org_dict["short_name"]}")

            reporting_org, created = ReportingOrg.objects.get_or_create(
                id=reporting_org_dict["id"],
            )
            reporting_org_ids_after.add(reporting_org.id)
            index_created = datetime.datetime.fromisoformat(metadata_reporting_orgs["index_created"])
            if not created and reporting_org.metadata_json_datetime > index_created:
                print(reporting_org.id, reporting_org.short_name)
                continue
            reporting_org.metadata_json_datetime = index_created
            reporting_org.human_readable_name = reporting_org_dict["human_readable_name"]
            reporting_org.short_name = reporting_org_dict["short_name"]
            reporting_org.metadata_json = reporting_org_dict
            reporting_org.save()

        reporting_org_ids_removed = reporting_org_ids_before - reporting_org_ids_after
        ReportingOrg.objects.filter(id__in=reporting_org_ids_removed).delete()

        dataset_ids_before = set(Dataset.objects.values_list("id", flat=True))
        dataset_ids_after = set()

        for dataset_dict in metadata_datasets["datasets"]:
            try:
                dup_dataset = Dataset.objects.get(short_name=dataset_dict["short_name"])
            except Dataset.DoesNotExist:
                pass
            else:
                if dup_dataset.id != uuid.UUID(dataset_dict["id"]):
                    dataset_ids_before.remove(dup_dataset.id)
                    dup_dataset.delete()
                    print(f"ERROR: duplicate Dataset short_name: {dataset_dict["short_name"]}")

            try:
                reporting_org = ReportingOrg.objects.get(short_name=dataset_dict["reporting_org_short_name"])
            except ReportingOrg.DoesNotExist:
                print("Reporting Org", dataset_dict["reporting_org_short_name"], "not found")
                continue
            dataset, created = Dataset.objects.get_or_create(
                id=dataset_dict["id"],
                reporting_org=reporting_org,
            )
            dataset_ids_after.add(dataset.id)
            index_created = datetime.datetime.fromisoformat(metadata_datasets["index_created"])
            if not created and dataset.metadata_json_datetime > index_created:
                print(
                    f"Skipping dataset with ID {dataset.id} ({dataset.short_name}), because it has been updated more recently than these metadata files."
                )
                continue
            dataset.short_name = dataset_dict["short_name"]
            dataset.source_url = dataset_dict["source_url"]
            dataset.metadata_json = dataset_dict
            dataset.metadata_json_datetime = index_created
            dataset.check_result_json = dataset_dict
            dataset.check_result_json_datetime = index_created
            dataset.save()

        dataset_ids_removed = dataset_ids_before - dataset_ids_after
        Dataset.objects.filter(id__in=dataset_ids_removed).delete()
