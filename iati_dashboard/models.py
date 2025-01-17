from django.db import models


class Publisher(models.Model):
    slug = models.CharField()
    title = models.CharField()
    stats_json = models.JSONField(default=dict)
    has_future_transactions = models.IntegerField(default=0)
    timeliness_frequency = models.JSONField(default=dict)
    forwardlooking = models.JSONField(default=dict)
    comprehensiveness = models.JSONField(default=dict)
    humanitarian = models.JSONField(default=dict)
    summary_stats = models.JSONField(default=dict)
    # too long
    traceable_sum_commitments_and_disbursements_by_publisher_id_den = models.GeneratedField(
        expression=models.F("stats_json__traceable_sum_commitments_and_disbursements_by_publisher_id_denominator"),
        output_field=models.JSONField(),
        db_persist=True,
    )

    @property
    def traceable_sum_commitments_and_disbursements_by_publisher_id_denominator(self):
        return self.traceable_sum_commitments_and_disbursements_by_publisher_id_den


for key in [
    "activities",
    "traceable_activities_by_publisher_id",
    "traceable_activities_by_publisher_id_denominator",
    "traceable_sum_commitments_and_disbursements_by_publisher_id",
]:
    Publisher.add_to_class(
        key,
        models.GeneratedField(
            expression=models.F(f"stats_json__{key}"), output_field=models.JSONField(), db_persist=True
        ),
    )
