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

from django.contrib import admin
from django.urls import path, re_path
from django.views.generic.base import RedirectView

import ui.views


urlpatterns = [
    path("admin/", admin.site.urls),
    # Top level dashboard pages.
    path("", ui.views.index, name="dash-index"),
    path("headlines", ui.views.headlines, name="dash-headlines"),
    path("data-quality", ui.views.data_quality, name="dash-dataquality"),
    path("publishing-statistics", ui.views.publishing_stats, name="dash-publishingstats"),
    path("exploring-data", ui.views.exploring_data, name="dash-exploringdata"),
    path("faq", ui.views.faq, name="dash-faq"),
    # Headlines pages and detail pages - placeholders for now.
    path("headlines/publishers", ui.views.headlines_publishers, name="dash-headlines-publishers"),
    path("headlines/files", ui.views.headlines_files, name="dash-headlines-files"),
    path("headlines/activities", ui.views.headlines_activities, name="dash-headlines-activities"),
    path(
        "headlines/publishers/<slug:publisher>",
        ui.views.headlines_publisher_detail,
        name="dash-headlines-publisher-detail",
    ),
    # Data quality pages.
    path("data-quality/download-errors", ui.views.dataquality_download, name="dash-dataquality-download"),
    path("data/download_errors.json", ui.views.dataquality_download_errorsjson, name="dash-dataquality-download-json"),
    path("data-quality/xml-errors", ui.views.dataquality_xml, name="dash-dataquality-xml"),
    path("data-quality/validation", ui.views.dataquality_validation, name="dash-dataquality-validation"),
    path("data-quality/versions", ui.views.dataquality_versions, name="dash-dataquality-versions"),
    path("data-quality/organisation", ui.views.dataquality_orgxml, name="dash-dataquality-organisation"),
    path("data-quality/licenses", ui.views.dataquality_licenses, name="dash-dataquality-licenses"),
    path(
        "data-quality/licenses/<slug:license_id>",
        ui.views.dataquality_licenses_detail,
        name="dash-dataquality-licenses-detail",
    ),
    path("data-quality/identifiers", ui.views.dataquality_identifiers, name="dash-dataquality-identifiers"),
    path("data-quality/reporting-orgs", ui.views.dataquality_reportingorgs, name="dash-dataquality-reportingorgs"),
    # Exploring data pages.
    path("exploring-data/elements", ui.views.exploringdata_elements, name="dash-exploringdata-elements"),
    path(
        "exploring-data/elements/<str:element>",
        ui.views.exploringdata_element_detail,
        name="dash-exploringdata-elements-detail",
    ),
    path("exploring-data/codelists", ui.views.exploringdata_codelists, name="dash-exploringdata-codelists"),
    path(
        "exploring-data/codelists/<str:major_version>/<str:attribute>",
        ui.views.exploringdata_codelists_detail,
        name="dash-exploringdata-codelists-detail",
    ),
    path("exploring-data/booleans", ui.views.exploringdata_booleans, name="dash-exploringdata-booleans"),
    path("exploring-data/dates", ui.views.exploringdata_dates, name="dash-exploringdata-dates"),
    path("exploring-data/traceability", ui.views.exploringdata_traceability, name="dash-exploringdata-traceability"),
    path("exploring-data/organisation-identifiers", ui.views.exploringdata_orgids, name="dash-exploringdata-orgids"),
    path(
        "exploring-data/organisation-type/<slug:org_type>",
        ui.views.exploringdata_orgtypes_detail,
        name="dash-exploringdata-orgtypes-detail",
    ),
    # Publishing statistics pages.
    path("publishing-statistics/timeliness", ui.views.pubstats_timeliness, name="dash-publishingstats-timeliness"),
    path(
        "publishing-statistics/timeliness-timelag",
        ui.views.pubstats_timeliness_timelag,
        name="dash-publishingstats-timeliness-timelag",
    ),
    path(
        "publishing-statistics/forward-looking",
        ui.views.pubstats_forwardlooking,
        name="dash-publishingstats-forwardlooking",
    ),
    path(
        "publishing-statistics/comprehensiveness",
        ui.views.pubstats_comprehensiveness,
        name="dash-publishingstats-comprehensiveness",
    ),
    path(
        "publishing-statistics/comprehensiveness/core",
        ui.views.pubstats_comprehensiveness_core,
        name="dash-publishingstats-comprehensiveness-core",
    ),
    path(
        "publishing-statistics/comprehensiveness/financials",
        ui.views.pubstats_comprehensiveness_financials,
        name="dash-publishingstats-comprehensiveness-financials",
    ),
    path(
        "publishing-statistics/comprehensiveness/value-added",
        ui.views.pubstats_comprehensiveness_valueadded,
        name="dash-publishingstats-comprehensiveness-valueadded",
    ),
    path(
        "publishing-statistics/summary-statistics",
        ui.views.pubstats_summarystats,
        name="dash-publishingstats-summarystats",
    ),
    path(
        "publishing-statistics/humanitarian-reporting",
        ui.views.pubstats_humanitarian,
        name="dash-publishingstats-humanitarian",
    ),
    # Registration agencies.
    path("registration-agencies", ui.views.registration_agencies, name="dash-registrationagencies"),
    path("registration_agencies.html", RedirectView.as_view(pattern_name="dash-registrationagencies", permanent=True)),
    # Redirects to support any users with bookmarks to pages on the old Dashboard.
    path("index.html", RedirectView.as_view(pattern_name="dash-index", permanent=True)),
    path("headlines.html", RedirectView.as_view(pattern_name="dash-headlines", permanent=True)),
    path("data_quality.html", RedirectView.as_view(pattern_name="dash-dataquality", permanent=True)),
    path("exploring_data.html", RedirectView.as_view(pattern_name="dash-exploringdata-elements", permanent=True)),
    path("publishers.html", RedirectView.as_view(pattern_name="dash-headlines-publishers", permanent=True)),
    path("publishing_stats.html", RedirectView.as_view(pattern_name="dash-publishingstats", permanent=True)),
    path("timeliness.html", RedirectView.as_view(pattern_name="dash-publishingstats-timeliness", permanent=True)),
    path(
        "timeliness_timelag.html",
        RedirectView.as_view(pattern_name="dash-publishingstats-timeliness-timelag", permanent=True),
    ),
    path(
        "forwardlooking.html", RedirectView.as_view(pattern_name="dash-publishingstats-forwardlooking", permanent=True)
    ),
    path(
        "comprehensiveness.html",
        RedirectView.as_view(pattern_name="dash-publishingstats-comprehensiveness", permanent=True),
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
    path("summary_stats.html", RedirectView.as_view(pattern_name="dash-publishingstats-summarystats", permanent=True)),
    path("humanitarian.html", RedirectView.as_view(pattern_name="dash-publishingstats-humanitarian", permanent=True)),
    path("files.html", RedirectView.as_view(pattern_name="dash-headlines-files", permanent=True)),
    path("activities.html", RedirectView.as_view(pattern_name="dash-headlines-activities", permanent=True)),
    path("download.html", RedirectView.as_view(pattern_name="dash-dataquality-download", permanent=True)),
    path("xml.html", RedirectView.as_view(pattern_name="dash-dataquality-xml", permanent=True)),
    path("validation.html", RedirectView.as_view(pattern_name="dash-dataquality-validation", permanent=True)),
    path("versions.html", RedirectView.as_view(pattern_name="dash-dataquality-versions", permanent=True)),
    path("organisation.html", RedirectView.as_view(pattern_name="dash-dataquality-organisation", permanent=True)),
    path("identifiers.html", RedirectView.as_view(pattern_name="dash-dataquality-identifiers", permanent=True)),
    path("reporting_orgs.html", RedirectView.as_view(pattern_name="dash-dataquality-reportingorgs", permanent=True)),
    path("elements.html", RedirectView.as_view(pattern_name="dash-exploringdata-elements", permanent=True)),
    path("codelists.html", RedirectView.as_view(pattern_name="dash-exploringdata-codelists", permanent=True)),
    path("booleans.html", RedirectView.as_view(pattern_name="dash-exploringdata-booleans", permanent=True)),
    path("dates.html", RedirectView.as_view(pattern_name="dash-exploringdata-dates", permanent=True)),
    path("traceability.html", RedirectView.as_view(pattern_name="dash-exploringdata-traceability", permanent=True)),
    path("org_ids.html", RedirectView.as_view(pattern_name="dash-exploringdata-orgids", permanent=True)),
    path("faq.html", RedirectView.as_view(pattern_name="dash-faq", permanent=True)),
    path("licenses.html", RedirectView.as_view(pattern_name="dash-dataquality-licenses", permanent=True)),
    re_path(r"license\/\S*.html", RedirectView.as_view(pattern_name="dash-dataquality-licenses", permanent=True)),
    re_path(r"publisher\/\S*.html", RedirectView.as_view(pattern_name="dash-headlines-publishers", permanent=True)),
    re_path(
        r"codelist\/\d\/\S*.html", RedirectView.as_view(pattern_name="dash-exploringdata-codelists", permanent=True)
    ),
    re_path(r"element\/\S*.html", RedirectView.as_view(pattern_name="dash-exploringdata-elements", permanent=True)),
    re_path(r"org_type\/\S*.html", RedirectView.as_view(pattern_name="dash-exploringdata-orgids", permanent=True)),
]
