import django_filters
from django.contrib.postgres.search import SearchQuery, SearchVector

from .data import codelist_lookup
from .models import ReportingOrg

COUNTRY_CODELIST_CHOICES = [(code, code_dict["name"]) for code, code_dict in codelist_lookup["2"]["Country"].items()]

FILE_TYPE_CHOICES = [("iati-activities", "Activities"), ("iati-organisations", "Organisations"), ("both", "Both")]


class ReportingOrgFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method="search_fulltext", label="Search reporting organisation name / registry ID"
    )
    hq_country = django_filters.ChoiceFilter(
        choices=COUNTRY_CODELIST_CHOICES, label="Reporting organisation HQ country"
    )

    recipient_country_code = django_filters.ChoiceFilter(
        choices=COUNTRY_CODELIST_CHOICES, lookup_expr="contains", label="Publishes files containing data about country"
    )
    file_types = django_filters.ChoiceFilter(
        choices=FILE_TYPE_CHOICES, lookup_expr="contains", label="Publishes files containing"
    )

    def search_fulltext(self, queryset, field_name, value):
        if not value:
            return queryset
        return queryset.annotate(search=SearchVector("short_name", "human_readable_name")).filter(
            search=SearchQuery(value)
        )

    class Meta:
        model = ReportingOrg
        fields = ["search", "hq_country", "recipient_country_code", "file_types"]
