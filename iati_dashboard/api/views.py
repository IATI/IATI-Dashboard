from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from ..filters import ReportingOrgFilter
from ..models import Dataset, ReportingOrg
from .serializers import DatasetSerializer, ReportingOrgSerializer


class LargeMaxPageNumberPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 1_000_000


class ReportingOrgViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows reporting orgs to be viewed.
    """

    queryset = ReportingOrg.objects.defer("stats_json").all().order_by("human_readable_name")
    serializer_class = ReportingOrgSerializer
    pagination_class = LargeMaxPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ReportingOrgFilter

    def retrieve(self, request, pk: str):
        user = get_object_or_404(self.queryset, short_name=pk)
        serializer = ReportingOrgSerializer(user)
        return Response(serializer.data)


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows reporting orgs to be viewed.
    """

    queryset = (
        Dataset.objects.all()
        .select_related("reporting_org")
        .only("short_name", "source_url", "registry_metadata_realtime", "reporting_org__short_name")
        .order_by("short_name")
    )
    serializer_class = DatasetSerializer
    pagination_class = LargeMaxPageNumberPagination

    def retrieve(self, request, pk: str):
        user = get_object_or_404(self.queryset, short_name=pk)
        serializer = DatasetSerializer(user)
        return Response(serializer.data)
