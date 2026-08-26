from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from ..filters import DatasetFilter, ReportingOrgFilter
from ..models import Dataset, ReportingOrg
from .serializers import DatasetSerializer, ReportingOrgSerializer


class LargeMaxPageNumberPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 1_000_000


@extend_schema_view(
    retrieve=extend_schema(
        description="Metadata for a single reporting organisation.",
        parameters=[OpenApiParameter("show_stats"), OpenApiParameter("show_stats_large")],
    )
)
class ReportingOrgViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Metadata about reporting organisations.
    """

    queryset = ReportingOrg.objects.defer("stats_json", "metadata_json").all().order_by("human_readable_name")
    serializer_class = ReportingOrgSerializer
    pagination_class = LargeMaxPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ReportingOrgFilter

    def retrieve(self, request, pk: str, **kwargs):
        user = get_object_or_404(self.queryset, short_name=pk)
        serializer = ReportingOrgSerializer(user, context=self.get_serializer_context())
        return Response(serializer.data)

    def get_serializer_context(self):
        return {
            "show_stats": self.request.GET.get("show_stats"),
            "show_stats_large": self.request.GET.get("show_stats_large"),
        }


@extend_schema_view(retrieve=extend_schema(description="Metadata for a single dataset."))
class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Metadata about datasets.
    """

    queryset = (
        Dataset.objects.all()
        .select_related("reporting_org")
        .only("short_name", "source_url", "licence_id", "reporting_org__short_name")
        .order_by("short_name")
    )
    serializer_class = DatasetSerializer
    pagination_class = LargeMaxPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DatasetFilter

    def retrieve(self, request, pk: str):
        user = get_object_or_404(self.queryset, short_name=pk)
        serializer = DatasetSerializer(user)
        return Response(serializer.data)
