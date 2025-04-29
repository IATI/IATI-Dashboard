from django.db import connection, models


class Publisher(models.Model):
    short_name = models.CharField()
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

    @property
    def traceable_sum_commitments_and_disbursements_by_publisher_id_denominator(self):
        return self.traceable_sum_commitments_and_disbursements_by_publisher_id_den

    def filtered_datasets_by(self, stat_name):
        return self.dataset_set.values("short_name", "source_url", f"stats_json__{stat_name}").filter(
            **{f"stats_json__{stat_name}__gt": 0}
        )

    def datasets_per(self, stat_name):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select keys, COUNT(id)
                from (
                    select jsonb_object_keys(stats_json->%s) as keys, id
                    from iati_dashboard_dataset
                    where publisher_id=%s
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
    Publisher.add_to_class(
        key,
        models.GeneratedField(
            expression=models.F(f"stats_json__{key}"), output_field=models.JSONField(), db_persist=True
        ),
    )


class Dataset(models.Model):
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    short_name = models.CharField()
    source_url = models.CharField()
    stats_json = models.JSONField(default=dict)
