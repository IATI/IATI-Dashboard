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
from django.urls import path
# from django.shortcuts import redirect

import ui.views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Top level dashboard pages.
    path('', ui.views.index, name="dash-index"),
    path('headlines', ui.views.headlines, name="dash-headlines"),
    path('data-quality', ui.views.data_quality, name="dash-dataquality"),
    path('publishing-statistics', ui.views.publishing_stats, name="dash-publishingstats"),
    path('exploring-data', ui.views.exploring_data, name="dash-exploringdata"),
    path('faq', ui.views.faq, name="dash-faq"),

    # Headlines pages and detail pages - placeholders for now.
    path('headlines/publishers', ui.views.headlines_publishers, name="dash-headlines-publishers"),
    path('headlines/files', ui.views.headlines_files, name="dash-headlines-files"),
    path('headlines/activities', ui.views.headlines_activities, name="dash-headlines-activities"),
    path('headlines/publishers/<slug:publisher>', ui.views.headlines_publisher_detail, name='dash-headlines-publisher-detail'),

    # Data quality pages.
    path('data-quality/download-errors', lambda x: None, name="dash-dataquality-download"),
    path('data-quality/xml-errors', lambda x: None, name="dash-dataquality-xml"),
    path('data-quality/validation', lambda x: None, name="dash-dataquality-validation"),
    path('data-quality/versions', lambda x: None, name="dash-dataquality-versions"),
    path('data-quality/organisation-xml', lambda x: None, name="dash-dataquality-organisation"),
    path('data-quality/licenses', ui.views.dataquality_licenses, name="dash-dataquality-licenses"),
    path('data-quality/licenses/<slug:license_id>', ui.views.dataquality_licenses_detail, name="dash-dataquality-licenses-detail"),
    path('data-quality/identifiers', lambda x: None, name="dash-dataquality-identifiers"),
    path('data-quality/reporting-orgs', lambda x: None, name="dash-dataquality-reportingorgs"),

    # Exploring data pages.
    path('exploring-data/elements', lambda x: None, name="dash-exploringdata-elements"),
    path('exploring-data/elements/<str:element>', lambda x: None, name="dash-exploringdata-elements-detail"),
    path('exploring-data/codelists', lambda x: None, name="dash-exploringdata-codelists"),
    path('exploring-data/codelists/<int:major_version>/<str:attribute>', lambda x: None, name="dash-exploringdata-codelists-detail"),
    path('exploring-data/booleans', lambda x: None, name="dash-exploringdata-booleans"),
    path('exploring-data/dates', lambda x: None, name="dash-exploringdata-dates"),
    path('exploring-data/traceability', lambda x: None, name="dash-exploringdata-traceability"),
    path('exploring-data/organisation-identifiers', lambda x: None, name="dash-exploringdata-orgids"),
    path('exploring-data/organisation-types/<slug:org_type>', lambda x: None, name="dash-exploringdata-orgtypes-detail"),

    # Publishing statistics pages.
    path('publishing-statistics/timeliness', lambda x: None, name="dash-publishingstats-timeliness"),
    path('publishing-statistics/forward-looking', lambda x: None, name="dash-publishingstats-forwardlooking"),
    path('publishing-statistics/comprehensiveness', lambda x: None, name="dash-publishingstats-comprehensiveness"),
    path('publishing-statistics/coverage', lambda x: None, name="dash-publishingstats-coverage"),
    path('publishing-statistics/summary-statistics', lambda x: None, name="dash-publishingstats-summarystats"),
    path('publishing-statistics/humanitarian-reporting', lambda x: None, name="dash-publishingstats-humanitarian"),

    # Redirects to support any users with bookmarks to pages on the old Dashboard.
    # path('timeliness.html', redirect("dash-publishingstats-timeliness")),
    # path('index.html', redirect("dash-index")),
    # path('summary_stats.html', redirect("dash-publishingstats-summarystats")),
    # path('exploring_data.html', redirect("dash-exploringdata"))

]
# Unsure where "rulesets" and "registration_agencies" should belong - can't find the route to these in make_html.py
