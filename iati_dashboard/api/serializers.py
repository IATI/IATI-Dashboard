from rest_framework import serializers

from ..models import REPORTING_ORG_METADATA_FIELDS, Dataset, ReportingOrg


class ReportingOrgSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ReportingOrg
        fields = ["id", "short_name", "human_readable_name", "dataset_count"]
        fields += REPORTING_ORG_METADATA_FIELDS


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    reporting_org_id = serializers.PrimaryKeyRelatedField(many=False, read_only=True, source="reporting_org")
    reporting_org_short_name = serializers.SlugRelatedField(
        many=False, read_only=True, source="reporting_org", slug_field="short_name"
    )

    class Meta:
        model = Dataset
        fields = ["id", "short_name", "source_url", "reporting_org_id", "reporting_org_short_name", "licence_id"]
