import requests
import yaml
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..models import REPORTING_ORG_METADATA_FIELDS, Dataset, ReportingOrg


class ReportingOrgSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReportingOrg
        fields = ["id", "short_name", "human_readable_name", "dataset_count"]
        fields += REPORTING_ORG_METADATA_FIELDS
        fields += ["stats"]

    stats = serializers.SerializerMethodField()

    @extend_schema_field(
        {
            "type": "object",
            "properties": yaml.safe_load(
                requests.get("https://raw.githubusercontent.com/IATI/IATI-Stats/refs/heads/stats-api/schema.yml").text
            ),
        }
    )
    def get_stats(self, reporting_org):
        if "show_stats" in self.context and self.context["show_stats"]:
            if "show_stats_large" in self.context and self.context["show_stats_large"]:
                return reporting_org.stats_json
            else:
                deleted_keys = [
                    "iati_identifiers",
                    "sum_commitments_and_disbursements_by_activity_id_usd",
                    "iati_identifiers_by_publisher_id",
                    "sum_commitments_and_disbursements_by_activity_id_by_publisher_id_usd",
                ]
                stats = {key: value for key, value in reporting_org.stats_json.items() if key not in deleted_keys}
                return stats


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    reporting_org_id = serializers.PrimaryKeyRelatedField(many=False, read_only=True, source="reporting_org")
    reporting_org_short_name = serializers.SlugRelatedField(
        many=False, read_only=True, source="reporting_org", slug_field="short_name"
    )

    class Meta:
        model = Dataset
        fields = ["id", "short_name", "source_url", "reporting_org_id", "reporting_org_short_name", "licence_id"]
