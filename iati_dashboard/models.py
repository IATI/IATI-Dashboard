import copy
import json
import uuid
from datetime import datetime, timezone
from enum import Enum

from django.db import connection, models

from . import filepaths

#  Import organisation_type_codelist as a global, then delete when used to save memory
with open(filepaths.join_data_path("IATI-Codelists-2/out/clv2/json/en/OrganisationType.json")) as fh:
    organisation_type_codelist = json.load(fh)
organisation_type_dict = {c["code"]: c["name"] for c in organisation_type_codelist["data"]}
del organisation_type_codelist


# From https://github.com/IATI/iati-account-web/blob/6f15fb301b3757d00fc0c83ff640e6e9bce104ad/iati_account_web/constants.py#L76-L77
REPORTING_SOURCE_TYPE_LIST = [("primary_source", "Primary Source"), ("secondary_source", "Secondary Source")]
REPORTING_SOURCE_TYPE_LOOKUP = {x[0]: x[1] for x in REPORTING_SOURCE_TYPE_LIST}


DEFAULT_STATS_JSON = {
    "activities": 0,
    "organisations": 0,
    "activity_files": 0,
    "organisation_files": 0,
    "file_size": 0,
    "hierarchies": {},
    "reporting_orgs": {},
}


def get_default_stats_json():
    return copy.deepcopy(DEFAULT_STATS_JSON)


class JSONTextField(models.JSONField):
    def db_type(self, connection):
        return "json"

    def from_db_value(self, value, expression, connection):
        # psycopg3 auto-decodes the `json` type (jsonb has a Django-side loader
        # that prevents this; plain json does not), so the parent's json.loads
        # is handed a dict and raises TypeError.
        if isinstance(value, (dict, list)):
            return value
        return super().from_db_value(value, expression, connection)


class ReportingOrg(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_name = models.CharField(unique=True)
    human_readable_name = models.CharField()

    metadata_json = models.JSONField(default=dict)
    metadata_json_datetime = models.DateTimeField(default=datetime(2000, 1, 1, 0, 0, 0, 0, timezone.utc))
    stats_json = models.JSONField(default=get_default_stats_json)

    has_future_transactions = models.IntegerField(default=0)
    timeliness_frequency = models.JSONField(default=dict)
    forwardlooking = models.JSONField(default=dict)
    comprehensiveness = models.JSONField(default=dict)
    humanitarian = models.JSONField(default=dict)
    summary_stats = models.JSONField(default=dict)
    validation_datasets = models.JSONField(default=dict)

    # too long
    traceable_sum_commitments_and_disbursements_by_publisher_id_den = models.GeneratedField(
        expression=models.F("stats_json__traceable_sum_commitments_and_disbursements_by_publisher_id_denominator"),
        output_field=models.JSONField(),
        db_persist=True,
    )

    recipient_country_code = models.JSONField(default=list)
    file_types = models.JSONField(default=list)

    @property
    def traceable_sum_commitments_and_disbursements_by_publisher_id_denominator(self):
        return self.traceable_sum_commitments_and_disbursements_by_publisher_id_den

    @property
    def dataset_count(self) -> int:
        return self.activity_files + self.organisation_files

    @property
    def organisation_type_name(self):
        return organisation_type_dict.get(self.organisation_type)

    @property
    def reporting_source_type_name(self):
        return REPORTING_SOURCE_TYPE_LOOKUP.get(self.reporting_source_type, "")

    def filtered_datasets_by(self, stat_name):
        return (
            self.dataset_set.order_by("short_name")
            .values("short_name", "source_url", f"stats_json__{stat_name}")
            .filter(**{f"stats_json__{stat_name}__gt": 0})
        )

    def datasets_per(self, stat_name):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select keys, COUNT(id)
                from (
                    select jsonb_object_keys(stats_json->%s) as keys, id
                    from iati_dashboard_dataset
                    where reporting_org_id=%s
                )
                group by keys;
            """,
                [stat_name, self.id],
            )
            return dict(cursor.fetchall())


for key in [
    "activities",
    "organisations",
    "activity_files",
    "organisation_files",
    "file_size",
    "hierarchies",
    "reporting_orgs",
    "traceable_activities_by_publisher_id",
    "traceable_activities_by_publisher_id_denominator",
    "traceable_sum_commitments_and_disbursements_by_publisher_id",
    "transaction_months_with_year",
    "timelag",
    "elements",
    "elements_total",
]:
    ReportingOrg.add_to_class(
        key,
        models.GeneratedField(
            expression=models.F(f"stats_json__{key}"), output_field=models.JSONField(), db_persist=True
        ),
    )


REPORTING_ORG_METADATA_FIELDS = [
    "created_date",
    "data_portal_url",
    "default_licence_id",
    "description",
    "exclusions_policy_url",
    "first_publication_date",
    "hq_country",
    "organisation_identifier",
    "organisation_type",
    "region",
    "reporting_source_type",
    "website",
]


for key in ["id", "short_name"]:
    ReportingOrg.add_to_class(
        f"reporting_org_{key}",
        models.GeneratedField(
            expression=models.F(f"metadata_json__{key}"), output_field=models.JSONField(), db_persist=True
        ),
    )


for key in REPORTING_ORG_METADATA_FIELDS:
    ReportingOrg.add_to_class(
        key,
        models.GeneratedField(
            expression=models.F(f"metadata_json__{key}"), output_field=models.JSONField(), db_persist=True
        ),
    )


class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporting_org = models.ForeignKey(ReportingOrg, on_delete=models.CASCADE)
    short_name = models.CharField(unique=True)
    source_url = models.CharField()
    most_recent_dataset_check_result = models.JSONField(default=dict)

    metadata_json = models.JSONField(default=dict)
    metadata_json_datetime = models.DateTimeField(default=datetime(2000, 1, 1, 0, 0, 0, 0, timezone.utc))
    check_result_json = models.JSONField(default=dict)
    check_result_json_datetime = models.DateTimeField(default=datetime(2000, 1, 1, 0, 0, 0, 0, timezone.utc))
    stats_json = models.JSONField(default=get_default_stats_json)


DATASET_METADATA_FIELDS = [
    "licence_id",
]


for key in DATASET_METADATA_FIELDS:
    Dataset.add_to_class(
        key,
        models.GeneratedField(
            expression=models.F(f"metadata_json__{key}"), output_field=models.JSONField(), db_persist=True
        ),
    )


for key in [
    "activities",
    "organisations",
    "file_size",
    "versions",
]:
    Dataset.add_to_class(
        key,
        models.GeneratedField(
            expression=models.F(f"stats_json__{key}"), output_field=models.JSONField(), db_persist=True
        ),
    )


class ReportingOrgEventTypes(Enum):
    REGISTRY_REPORTING_ORG_RECORD_CREATED = (
        "REGISTRY_REPORTING_ORG_RECORD_CREATED",
        "Reporting Org record created on the IATI Registry",
    )
    REGISTRY_REPORTING_ORG_RECORD_UPDATED = (
        "REGISTRY_REPORTING_ORG_RECORD_UPDATED",
        "Reporting Org record updated on the IATI Registry",
    )
    REGISTRY_REPORTING_ORG_RECORD_DELETED = (
        "REGISTRY_REPORTING_ORG_RECORD_DELETED",
        "Reporting Org record deleted on the IATI Registry",
    )


class ReportingOrgEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(db_index=True)
    reporting_org_id = models.UUIDField(db_index=True)
    initiating_user_id = models.UUIDField(null=True)
    initiating_user_name = models.CharField(null=True)
    initiating_application_id = models.UUIDField(null=True)
    initiating_application_name = models.CharField(null=True)
    initiating_organisation_id = models.UUIDField(null=True)
    initiating_organisation_name = models.UUIDField(null=True)
    event_type = models.CharField(
        max_length=50, choices=[(option.value[0], option.value[1]) for option in ReportingOrgEventTypes]
    )
    message_payload = models.CharField()
    data_fields_current = models.JSONField()
    data_fields_previous = models.JSONField(null=True)


class DatasetEventTypes(Enum):
    REGISTRY_RECORD_CREATED = "REGISTRY_DATASET_RECORD_CREATED", "Dataset record created on the IATI Registry"
    REGISTRY_RECORD_UPDATED = "REGISTRY_DATASET_RECORD_UPDATED", "Dataset record updated on the IATI Registry"
    REGISTRY_RECORD_DELETED = "REGISTRY_DATASET_RECORD_DELETED", "Dataset record deleted on the IATI Registry"
    DATASET_DOWNLOAD_STATUS_CHANGED = "DOWNLOAD_STATUS_CHANGED", "Dataset download status changed"
    DATASET_CONTENT_CHANGED = "DATASET_CONTENT_CHANGED", "Dataset content changed"


class DatasetEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(db_index=True)
    dataset_id = models.UUIDField(db_index=True)
    reporting_org_id = models.UUIDField(db_index=True)
    initiating_user_id = models.UUIDField(null=True)
    initiating_user_name = models.CharField(null=True)
    initiating_application_id = models.UUIDField(null=True)
    initiating_application_name = models.CharField(null=True)
    initiating_organisation_id = models.UUIDField(null=True)
    initiating_organisation_name = models.UUIDField(null=True)
    event_type = models.CharField(
        max_length=50, choices=[(option.value[0], option.value[1]) for option in DatasetEventTypes]
    )
    message_payload = models.CharField()
    data_fields_current = models.JSONField()
    data_fields_previous = models.JSONField(null=True)


class DatasetHistoricEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message_type = models.CharField(null=False, db_index=True)
    display_category = models.CharField(null=False, db_index=True)
    message_date = models.DateTimeField(db_index=True)
    dataset_id = models.UUIDField(db_index=True)
    payload = JSONTextField()

    class Meta:
        db_table = "dataset_activity_stream"
        managed = False
