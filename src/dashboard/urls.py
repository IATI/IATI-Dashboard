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

import dashboard.views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Top level dashboard pages.
    path('', dashboard.views.index, name="dash-index"),
    path('headlines', dashboard.views.headlines, name="dash-headlines"),
    path('data-quality', dashboard.views.data_quality, name="dash-dataquality"),
    path('publishing-statistics', dashboard.views.publishing_stats, name="dash-publishingstats"),
    path('exploring-data', dashboard.views.exploring_data, name="dash-exploringdata"),
    path('faq', dashboard.views.faq, name="dash-faq"),

    # Headlines pages and detail pages - placeholders for now.
    path('headlines/publishers', dashboard.views.headlines_publishers, name="dash-headlines-publishers"),
    path('headlines/files', dashboard.views.headlines_files, name="dash-headlines-files"),
    path('headlines/activities', dashboard.views.headlines_activities, name="dash-headlines-activities"),
    path('headlines/publishers/<slug:publisher>', dashboard.views.headlines_publisher_detail, name='dash-headlines-publisher-detail'),

    # Data quality pages.
    path('data-quality/download-errors', lambda x: None, name="dash-dataquality-download"),
    path('data-quality/xml-errors', lambda x: None, name="dash-dataquality-xml"),
    path('data-quality/validation', lambda x: None, name="dash-dataquality-validation"),
    path('data-quality/versions', lambda x: None, name="dash-dataquality-versions"),
    path('data-quality/organisation-xml', lambda x: None, name="dash-dataquality-organisation"),
    path('data-quality/licenses', lambda x: None, name="dash-dataquality-licenses"),
    path('data-quality/identifiers', lambda x: None, name="dash-dataquality-identifiers"),
    path('data-quality/reporting-orgs', lambda x: None, name="dash-dataquality-reportingorgs"),

    # Exploring data pages.
    path('exploring-data/elements', lambda x: None, name="dash-exploringdata-elements"),
    path('exploring-data/codelists', lambda x: None, name="dash-exploringdata-codelists"),
    path('exploring-data/booleans', lambda x: None, name="dash-exploringdata-booleans"),
    path('exploring-data/dates', lambda x: None, name="dash-exploringdata-dates"),
    path('exploring-data/traceability', lambda x: None, name="dash-exploringdata-traceability"),
    path('exploring-data/organisation-identifiers', lambda x: None, name="dash-exploringdata-orgids"),

    # Publishing statistics pages.
    path('publishing-statistics/timeliness', lambda x: None, name="dash-publishingstats-timeliness"),
    path('publishing-statistics/forward-looking', lambda x: None, name="dash-publishingstats-forwardlooking"),
    path('publishing-statistics/comprehensiveness', lambda x: None, name="dash-publishingstats-comprehensiveness"),
    path('publishing-statistics/coverage', lambda x: None, name="dash-publishingstats-coverage"),
    path('publishing-statistics/summary-statistics', lambda x: None, name="dash-publishingstats-summarystats"),
    path('publishing-statistics/humanitarian-reporting', lambda x: None, name="dash-publishingstats-humanitarian"),

    # Licenses
    path('licenses/<slug:licence_id>', lambda x: None, name="dash-licence-detail"),
    path('licenses', lambda x: None, name="dash-licences")

    # Redirects to support any users with bookmarks to pages on the old Dashboard.
    # path('timeliness.html', redirect("dash-publishingstats-timeliness")),
    # path('index.html', redirect("dash-index")),
    # path('summary_stats.html', redirect("dash-publishingstats-summarystats")),
    # path('exploring_data.html', redirect("dash-exploringdata"))

]
# Unsure where "rulesets" and "registration_agencies" should belong - can't find the route to these in make_html.py
