"""
URL configuration for IATI Dashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = (
    [
        # Top level dashboard pages.
        path("", views.index, name="dash-index"),
        path("publishers/", views.headlines_publishers, name="dash-headlines-publishers"),
        path(
            "publishers/<slug:publisher_short_name>/",
            views.headlines_publisher_detail,
            name="dash-headlines-publisher-detail",
        ),
        path(
            "publishers/<slug:publisher_short_name>/codelists/<str:major_version>/<str:attribute>/",
            views.exploringdata_publisher_codelist_detail,
            name="dash-publisher-codelist-detail",
        ),
        path("errors/", views.errors, name="dash-errors"),
        path("publishing-statistics/", views.publishing_stats, name="dash-publishingstats"),
        path("exploring-data/", views.exploring_data, name="dash-exploringdata"),
        path("faq/", views.faq, name="dash-faq"),
        # Errors pages.
        path("errors/download-errors/", views.errors_download, name="dash-errors-download"),
        path("errors/xml-errors/", views.errors_xml, name="dash-errors-xml"),
        path("errors/validation/", views.errors_validation, name="dash-errors-validation"),
        path("errors/identifiers/", views.errors_identifiers, name="dash-identifiers"),
        path("errors/reporting-orgs/", views.errors_reportingorgs, name="dash-errors-reportingorgs"),
        # Exploring data pages.
        path("exploring-data/files/", views.headlines_files, name="dash-headlines-files"),
        path("exploring-data/activities/", views.headlines_activities, name="dash-headlines-activities"),
        path("exploring-data/elements/", views.exploringdata_elements, name="dash-exploringdata-elements"),
        path(
            "exploring-data/elements/<str:element>/",
            views.exploringdata_element_detail,
            name="dash-exploringdata-elements-detail",
        ),
        path("exploring-data/codelists/", views.exploringdata_codelists, name="dash-exploringdata-codelists"),
        path(
            "exploring-data/codelists/<str:major_version>/<str:attribute>/",
            views.exploringdata_codelists_detail,
            name="dash-exploringdata-codelists-detail",
        ),
        path("exploring-data/booleans/", views.exploringdata_booleans, name="dash-exploringdata-booleans"),
        path("exploring-data/dates/", views.exploringdata_dates, name="dash-exploringdata-dates"),
        path("exploring-data/versions/", views.versions, name="dash-versions"),
        path("exploring-data/organisation/", views.orgxml, name="dash-organisation"),
        path("exploring-data/licenses/", views.licenses, name="dash-licenses"),
        path("exploring-data/licenses/<str:license_id>/", views.licenses_detail, name="dash-licenses-detail"),
        path("exploring-data/traceability/", views.exploringdata_traceability, name="dash-exploringdata-traceability"),
        path("exploring-data/organisation-identifiers/", views.exploringdata_orgids, name="dash-exploringdata-orgids"),
        path(
            "exploring-data/organisation-type/<slug:org_type>/",
            views.exploringdata_orgtypes_detail,
            name="dash-exploringdata-orgtypes-detail",
        ),
        # Publishing statistics pages.
        path(
            "publishing-statistics/timeliness-frequency/",
            views.pubstats_timeliness_frequency,
            name="dash-publishingstats-timeliness-frequency",
        ),
        path(
            "publishing-statistics/timeliness-timelag/",
            views.pubstats_timeliness_timelag,
            name="dash-publishingstats-timeliness-timelag",
        ),
        path(
            "publishing-statistics/forward-looking/",
            views.pubstats_forwardlooking,
            name="dash-publishingstats-forwardlooking",
        ),
        path(
            "publishing-statistics/comprehensiveness-summary/",
            views.pubstats_comprehensiveness_summary,
            name="dash-publishingstats-comprehensiveness-summary",
        ),
        path(
            "publishing-statistics/comprehensiveness-core/",
            views.pubstats_comprehensiveness_core,
            name="dash-publishingstats-comprehensiveness-core",
        ),
        path(
            "publishing-statistics/comprehensiveness-financials/",
            views.pubstats_comprehensiveness_financials,
            name="dash-publishingstats-comprehensiveness-financials",
        ),
        path(
            "publishing-statistics/comprehensiveness-value-added/",
            views.pubstats_comprehensiveness_valueadded,
            name="dash-publishingstats-comprehensiveness-valueadded",
        ),
        path(
            "publishing-statistics/summary-statistics/",
            views.pubstats_summarystats,
            name="dash-publishingstats-summarystats",
        ),
        path(
            "publishing-statistics/humanitarian-reporting/",
            views.pubstats_humanitarian,
            name="dash-publishingstats-humanitarian",
        ),
        # Registration agencies.
        path("registration-agencies/", views.registration_agencies, name="dash-registrationagencies"),
        path(
            "registration_agencies.html",
            RedirectView.as_view(pattern_name="dash-registrationagencies", permanent=True),
        ),
        # Redirects to support any users with bookmarks to pages on the old Dashboard.
        path("index.html", RedirectView.as_view(pattern_name="dash-index", permanent=True)),
        # We've remove the headlines page, so redirect to the index
        path("headlines.html", RedirectView.as_view(pattern_name="dash-index", permanent=True)),
        path("data_quality.html", RedirectView.as_view(pattern_name="dash-errors", permanent=True)),
        path("exploring_data.html", RedirectView.as_view(pattern_name="dash-exploringdata-elements", permanent=True)),
        path("publishers.html", RedirectView.as_view(pattern_name="dash-headlines-publishers", permanent=True)),
        path("publishing_stats.html", RedirectView.as_view(pattern_name="dash-publishingstats", permanent=True)),
        path(
            "timeliness.html",
            RedirectView.as_view(pattern_name="dash-publishingstats-timeliness-frequency", permanent=True),
        ),
        path(
            "timeliness_timelag.html",
            RedirectView.as_view(pattern_name="dash-publishingstats-timeliness-timelag", permanent=True),
        ),
        path(
            "forwardlooking.html",
            RedirectView.as_view(pattern_name="dash-publishingstats-forwardlooking", permanent=True),
        ),
        path(
            "comprehensiveness.html",
            RedirectView.as_view(pattern_name="dash-publishingstats-comprehensiveness-summary", permanent=True),
        ),
        path(
            "comprehensiveness_core.html",
            RedirectView.as_view(pattern_name="dash-publishingstats-comprehensiveness-core", permanent=True),
        ),
        path(
            "comprehensiveness_financials.html",
            RedirectView.as_view(pattern_name="dash-publishingstats-comprehensiveness-financials", permanent=True),
        ),
        path(
            "comprehensiveness_valueadded.html",
            RedirectView.as_view(pattern_name="dash-publishingstats-comprehensiveness-valueadded", permanent=True),
        ),
        path(
            "summary_stats.html",
            RedirectView.as_view(pattern_name="dash-publishingstats-summarystats", permanent=True),
        ),
        path(
            "humanitarian.html", RedirectView.as_view(pattern_name="dash-publishingstats-humanitarian", permanent=True)
        ),
        path("files.html", RedirectView.as_view(pattern_name="dash-headlines-files", permanent=True)),
        path("activities.html", RedirectView.as_view(pattern_name="dash-headlines-activities", permanent=True)),
        path("download.html", RedirectView.as_view(pattern_name="dash-errors-download", permanent=True)),
        path("xml.html", RedirectView.as_view(pattern_name="dash-errors-xml", permanent=True)),
        path("validation.html", RedirectView.as_view(pattern_name="dash-errors-validation", permanent=True)),
        path("versions.html", RedirectView.as_view(pattern_name="dash-versions", permanent=True)),
        path("organisation.html", RedirectView.as_view(pattern_name="dash-organisation", permanent=True)),
        path("identifiers.html", RedirectView.as_view(pattern_name="dash-identifiers", permanent=True)),
        path("reporting_orgs.html", RedirectView.as_view(pattern_name="dash-errors-reportingorgs", permanent=True)),
        path("elements.html", RedirectView.as_view(pattern_name="dash-exploringdata-elements", permanent=True)),
        path("codelists.html", RedirectView.as_view(pattern_name="dash-exploringdata-codelists", permanent=True)),
        path("booleans.html", RedirectView.as_view(pattern_name="dash-exploringdata-booleans", permanent=True)),
        path("dates.html", RedirectView.as_view(pattern_name="dash-exploringdata-dates", permanent=True)),
        path(
            "traceability.html", RedirectView.as_view(pattern_name="dash-exploringdata-traceability", permanent=True)
        ),
        path("org_ids.html", RedirectView.as_view(pattern_name="dash-exploringdata-orgids", permanent=True)),
        path("faq.html", RedirectView.as_view(pattern_name="dash-faq", permanent=True)),
        path("licenses.html", RedirectView.as_view(pattern_name="dash-licenses", permanent=True)),
        re_path(r"license\/(\S*).html", RedirectView.as_view(pattern_name="dash-licenses-detail", permanent=True)),
        re_path(
            r"publisher\/(\S*).html",
            RedirectView.as_view(pattern_name="dash-headlines-publisher-detail", permanent=True),
        ),
        re_path(
            r"codelist\/(\d)\/(\S*).html",
            RedirectView.as_view(pattern_name="dash-exploringdata-codelists-detail", permanent=True),
        ),
        re_path(
            r"element\/(\S*).html",
            RedirectView.as_view(pattern_name="dash-exploringdata-elements-detail", permanent=True),
        ),
        re_path(
            r"org_type\/(\S*).html",
            RedirectView.as_view(pattern_name="dash-exploringdata-orgtypes-detail", permanent=True),
        ),
        path(
            "<slug:file_start>.csv",
            RedirectView.as_view(url="/generated/data/csv/%(file_start)s.csv", permanent=False),
        ),
    ]
    + static("generated", document_root="out")
    + static("stats", document_root="stats-calculated")
)
# ^ Serve generated files when using runserver for development

if settings.ENABLE_API_ALPHA:
    urlpatterns.append(path("api/", include("iati_dashboard.api.urls")))
