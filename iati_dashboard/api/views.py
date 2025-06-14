from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from ..models import Dataset, ReportingOrg
from .serializers import DatasetSerializer, ReportingOrgSerializer


class ReportingOrgViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows reporting orgs to be viewed.
    """

    queryset = ReportingOrg.objects.defer("stats_json").all().order_by("human_readable_name")
    serializer_class = ReportingOrgSerializer

    def retrieve(self, request, pk: str):
        user = get_object_or_404(self.queryset, short_name=pk)
        serializer = ReportingOrgSerializer(user)
        return Response(serializer.data)


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows reporting orgs to be viewed.
    """

    queryset = Dataset.objects.all().order_by("short_name")
    serializer_class = DatasetSerializer

    def retrieve(self, request, pk: str):
        user = get_object_or_404(self.queryset, short_name=pk)
        serializer = DatasetSerializer(user)
        return Response(serializer.data)
