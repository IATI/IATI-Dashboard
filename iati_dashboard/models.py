import uuid
from enum import Enum

from django.db import connection, models


class ReportingOrg(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_name = models.CharField(unique=True)
    human_readable_name = models.CharField()
    stats_json = models.JSONField(default=dict)
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

    @property
    def traceable_sum_commitments_and_disbursements_by_publisher_id_denominator(self):
        return self.traceable_sum_commitments_and_disbursements_by_publisher_id_den

    @property
    def dataset_count(self):
        return self.activity_files + self.organisation_files

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


class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporting_org = models.ForeignKey(ReportingOrg, on_delete=models.CASCADE)
    short_name = models.CharField(unique=True)
    source_url = models.CharField()
    most_recent_dataset_check_result = models.JSONField(default=dict)
    stats_json = models.JSONField(default=dict)


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
