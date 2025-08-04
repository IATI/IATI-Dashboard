import django_filters
from django.contrib.postgres.search import SearchQuery, SearchVector

from .data import codelist_lookup
from .models import ReportingOrg

COUNTRY_CODELIST_CHOICES = [(code, code_dict["name"]) for code, code_dict in codelist_lookup["2"]["Country"].items()]


class ReportingOrgFilter(django_filters.FilterSet):
    recipient_country_code = django_filters.ChoiceFilter(choices=COUNTRY_CODELIST_CHOICES, lookup_expr="contains")
    search = django_filters.CharFilter(method="search_fulltext", label="Search names")

    def search_fulltext(self, queryset, field_name, value):
        if not value:
            return queryset
        return queryset.annotate(search=SearchVector("short_name", "human_readable_name")).filter(
            search=SearchQuery(value)
        )

    class Meta:
        model = ReportingOrg
        fields = ["search", "recipient_country_code"]
