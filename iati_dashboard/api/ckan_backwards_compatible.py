from django.urls import path
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, serializers
from rest_framework.exceptions import APIException
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from ..models import Dataset, ReportingOrg


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class FiltersNotImplemented(APIException):
    status_code = 400
    default_detail = "Sorry, the filters used are not implemented."
    default_code = "bad_request"


class CBCPagination(LimitOffsetPagination):
    default_limit = 1_000_000

    def get_paginated_response(self, data):
        return Response({"success": True, "result": data})


class CBCDatasetSearchPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 1000
    limit_query_param = "rows"
    offset_query_param = "start"

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "result": {
                    "count": self.count,
                    "results": data,
                },
            }
        )


class CBCReportingOrgSerializer(serializers.Serializer):
    description = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    is_organization = serializers.SerializerMethodField()
    license_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    package_count = serializers.SerializerMethodField()
    publisher_country = serializers.SerializerMethodField()
    publisher_description = serializers.SerializerMethodField()
    publisher_first_publish_date = serializers.SerializerMethodField()
    publisher_iati_id = serializers.SerializerMethodField()
    publisher_organization_type = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    image_display_url = serializers.SerializerMethodField(method_name="return_null")
    image_url = serializers.SerializerMethodField(method_name="return_null")
    publisher_agencies = serializers.SerializerMethodField(method_name="return_null")
    publisher_constraints = serializers.SerializerMethodField(method_name="return_null")
    publisher_contact = serializers.SerializerMethodField(method_name="return_null")
    publisher_contact_email = serializers.SerializerMethodField(method_name="return_null")
    publisher_data_quality = serializers.SerializerMethodField(method_name="return_null")
    publisher_field_exclusions = serializers.SerializerMethodField(method_name="return_null")
    publisher_frequency = serializers.SerializerMethodField(method_name="return_null")
    publisher_frequency_select = serializers.SerializerMethodField(method_name="return_null")
    publisher_implementation_schedule = serializers.SerializerMethodField(method_name="return_null")
    publisher_record_exclusions = serializers.SerializerMethodField(method_name="return_null")
    publisher_refs = serializers.SerializerMethodField(method_name="return_null")
    publisher_segmentation = serializers.SerializerMethodField(method_name="return_null")
    publisher_source_type = serializers.SerializerMethodField(method_name="return_null")
    publisher_thresholds = serializers.SerializerMethodField(method_name="return_null")
    publisher_timeliness = serializers.SerializerMethodField(method_name="return_null")
    publisher_ui = serializers.SerializerMethodField(method_name="return_null")

    tags = serializers.SerializerMethodField(method_name="return_empty_list")
    groups = serializers.SerializerMethodField(method_name="return_empty_list")
    users = serializers.SerializerMethodField(method_name="return_empty_list")
    historical_publisher_names = serializers.SerializerMethodField(method_name="return_empty_list")

    def return_null(self, instance) -> None:
        return None

    def return_empty_list(self, instance) -> list:
        return []

    def get_description(self, instance) -> str:
        return ""

    def get_id(self, instance) -> str:
        return instance.id

    def get_license_id(self, instance) -> str:
        return instance.default_licence_id

    def get_is_organization(self, instance) -> bool:
        return True

    def get_name(self, instance) -> str:
        return instance.short_name

    def get_package_count(self, instance) -> int:
        return instance.dataset_count

    def get_publisher_country(self, instance) -> str:
        return instance.hq_country

    def get_publisher_description(self, instance) -> str:
        return instance.description

    def get_publisher_first_publish_date(self, instance) -> str:
        return instance.first_publication_date

    def get_publisher_iati_id(self, instance) -> str:
        return instance.organisation_identifier

    def get_publisher_organization_type(self, instance) -> str:
        return instance.organisation_type

    def get_state(self, instance) -> str:
        return "active"

    def get_title(self, instance) -> str:
        return instance.human_readable_name

    def get_type(self, instance) -> str:
        return "organization"


class CBCReportingOrgShortNameOnlySerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance.short_name


class CBCWrappedReportingOrgSerializer(serializers.Serializer):
    success = serializers.SerializerMethodField()
    result = CBCReportingOrgSerializer(source="*", many=False)

    def get_success(self, instance) -> bool:
        return True


class CBCDatasetSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    license_id = serializers.SerializerMethodField()
    license_title = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    num_resources = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    owner_org = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    extras = serializers.SerializerMethodField()
    resources = serializers.SerializerMethodField()
    publisher_source_type = serializers.SerializerMethodField()
    publisher_organization_type = serializers.SerializerMethodField()
    publisher_iati_id = serializers.SerializerMethodField()
    publisher_country = serializers.SerializerMethodField()

    author = serializers.SerializerMethodField(method_name="return_null")
    author_email = serializers.SerializerMethodField(method_name="return_null")
    creator_user_id = serializers.SerializerMethodField(method_name="return_null")
    maintainer = serializers.SerializerMethodField(method_name="return_null")
    maintainer_email = serializers.SerializerMethodField(method_name="return_null")

    def return_null(self, instance) -> None:
        return None

    def get_id(self, instance) -> str:
        return instance.id

    def get_license_id(self, instance) -> str:
        return instance.licence_id

    def get_license_title(self, instance) -> str:
        return ""

    def get_name(self, instance) -> str:
        return instance.short_name

    def get_num_resources(self, instance) -> int:
        return 1

    def get_organization(self, instance) -> dict:
        return {
            "id": instance.reporting_org.id,
            "name": instance.reporting_org.short_name,
            "title": instance.reporting_org.human_readable_name,
            "type": "organization",
            "description": "",
            "is_organization": True,
            "approval_status": "approved",
            "state": "active",
            "created": instance.reporting_org.created_date,
            "image_url": None,
        }

    def get_owner_org(self, instance) -> str:
        return instance.reporting_org.id

    def get_private(self, instance) -> bool:
        return False

    def get_state(self, instance) -> str:
        return "active"

    def get_title(self, instance) -> str:
        return instance.short_name

    def get_type(self, instance) -> str:
        return "dataset"

    def get_extras(self, instance) -> list:
        if instance.stats_json.get("organisation_files"):
            filetype = "organisation"
        elif instance.stats_json.get("activity_files"):
            filetype = "activity"
        else:
            filetype = None

        if filetype == "activity":
            extras = [{"key": "activity_count", "value": instance.stats_json.get("activities")}]
        else:
            extras = []
        extras += [
            {"key": "country", "value": None},
            {"key": "data_updated", "value": None},
            {"key": "filetype", "value": filetype},
            {"key": "iati_version", "value": (list(instance.stats_json.get("versions", {}).keys()) or [None])[0]},
            {"key": "language", "value": None},
            {"key": "secondary_publisher", "value": None},
            {"key": "validation_status", "value": None},
        ]
        return extras

    def get_resources(self, instance) -> list:
        return [
            {
                # None/null within resource is also always null in the original CKAN responses
                "cache_last_updated": None,
                "cache_url": None,
                "created": "",
                "description": "",
                "format": "IATI-XML",
                "hash": instance.metadata_json.get("last_known_good_dataset", {}).get(
                    "hash_excluding_generated_timestamp"
                ),
                "id": instance.id,
                "last_modified": None,
                # except for this one
                "metadata_modified": None,
                "mimetype": "application/xml",
                "mimetype_inner": None,
                "name": None,
                "package_id": instance.id,
                "position": 0,
                "resource_type": None,
                # except for this one
                "revision_id": None,
                "size": instance.metadata_json.get("last_known_good_dataset", {}).get("content_length"),
                "state": "active",
                "url": instance.source_url,
                "url_type": None,
            }
        ]

    def get_publisher_source_type(self, instance) -> str:
        return ""

    def get_publisher_organization_type(self, instance) -> str:
        return instance.reporting_org.organisation_type

    def get_publisher_iati_id(self, instance) -> str:
        return instance.reporting_org.organisation_identifier

    def get_publisher_country(self, instance) -> str:
        return instance.reporting_org.hq_country


class CBCWrappedDatasetSerializer(serializers.Serializer):
    success = serializers.SerializerMethodField()
    result = CBCDatasetSerializer(source="*", many=False)

    def get_success(self, instance) -> bool:
        return True


class CBCDatasetShortNameOnlySerializer(serializers.Serializer):
    def to_representation(self, instance):
        return instance.short_name


class AllowPost:
    @extend_schema(request={})
    def post(self, request, *args, **kwargs):
        return self.get(self, request, *args, **kwargs)


@extend_schema_view(get=(extend_schema(parameters=[OpenApiParameter("all_fields")])))
class OrganisationListView(generics.ListAPIView, AllowPost):
    renderer_classes = [JSONRenderer]

    queryset = ReportingOrg.objects.defer("stats_json").all().order_by("short_name")
    pagination_class = CBCPagination

    def get_serializer_class(self):
        all_fields = str2bool(self.request.GET.get("all_fields", ""))
        if all_fields:
            return CBCReportingOrgSerializer
        else:
            return CBCReportingOrgShortNameOnlySerializer


@extend_schema_view(get=(extend_schema(parameters=[OpenApiParameter("id")])))
class OrganisationRetrieveView(generics.RetrieveAPIView, AllowPost):
    renderer_classes = [JSONRenderer]
    serializer_class = CBCWrappedReportingOrgSerializer

    def get_object(self):
        return ReportingOrg.objects.get(short_name=self.request.GET.get("id", ""))


class PackageListView(generics.ListAPIView, AllowPost):
    renderer_classes = [JSONRenderer]

    queryset = Dataset.objects.defer("stats_json").all().order_by("short_name")
    pagination_class = CBCPagination
    serializer_class = CBCDatasetShortNameOnlySerializer


@extend_schema_view(get=(extend_schema(parameters=[OpenApiParameter("fq")])))
class PackageSearchView(generics.ListAPIView, AllowPost):
    """
    Only a minimal part of this endpoint has been implemented.
    We support pagination, and a limited set of queries to the q and fq arguments.
    Only these field names are supported: organization, owner_org, publisher_iati_id, extras_filetype
    And, they can be combined with " AND "
    """

    renderer_classes = [JSONRenderer]

    pagination_class = CBCDatasetSearchPagination
    serializer_class = CBCDatasetSerializer

    def get_queryset(self):
        datasets = (
            Dataset.objects.all()
            .prefetch_related("reporting_org")
            .defer("reporting_org__stats_json", "reporting_org__metadata_json")
        )
        q = self.request.GET.get("q", self.request.POST.get("q"))
        fq = self.request.GET.get("fq", self.request.POST.get("fq"))

        query_tokens = []
        if q:
            query_tokens += q.split(" AND ")
        if fq:
            query_tokens += fq.split(" AND ")

        for query_token in query_tokens:
            if " " in query_token or query_token.count(":") != 1:
                raise FiltersNotImplemented(
                    "This compatibility layer does not support this particular kind of query within the q or fq parameter."
                )
            query_key, query_value = query_token.split(":")
            if query_key == "organization":
                datasets = datasets.filter(reporting_org__short_name=query_value)
            elif query_key == "owner_org":
                datasets = datasets.filter(reporting_org__id=query_value)
            elif query_key == "publisher_iati_id":
                datasets = datasets.filter(reporting_org__organisation_identifier=query_value)
            elif query_key == "extras_filetype":
                if query_value == "activity":
                    datasets = datasets.filter(stats_json__activity_files__gte=1)
                elif query_value == "organisation":
                    datasets = datasets.filter(stats_json__organisation_files__gte=1)
                else:
                    datasets = []
            else:
                raise FiltersNotImplemented(
                    "This comptibility layer only supports these field names within the q or fq parameter: organization, owner_org, publisher_iati_id, extras_filetype"
                )
        return datasets


@extend_schema_view(get=(extend_schema(parameters=[OpenApiParameter("id")])))
class PackageRetrieveView(generics.RetrieveAPIView, AllowPost):
    renderer_classes = [JSONRenderer]
    pagination_class = CBCPagination
    serializer_class = CBCWrappedDatasetSerializer

    def get_object(self):
        return Dataset.objects.get(short_name=self.request.GET.get("id", ""))


urlpatterns = [
    path("organization_list", OrganisationListView.as_view()),
    path("organization_show", OrganisationRetrieveView.as_view()),
    # This is a duplicate of organisation_show, and has been deprecated in CKAN, but not removed
    # We know that at least iatikit relies on it
    path("group_list", OrganisationListView.as_view()),
    path("group_show", OrganisationRetrieveView.as_view()),
    path("package_list", PackageListView.as_view()),
    path("package_search", PackageSearchView.as_view()),
    path("package_show", PackageRetrieveView.as_view()),
]
