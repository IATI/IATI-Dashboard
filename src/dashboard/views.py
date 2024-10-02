"""Views for the IATI Dashboard"""

# Note: in the page views I am unsure where "rulesets" and "registration_agencies" should
# belong - they exist in text.page_tiles but I can't find the route to these in make_html.py
# so not sure where they should fit.  I've not included them in the page_view_names so hopefully
# an exception will be raised if they are referenced somewhere.

import dateutil.parser
import subprocess

from django.http import HttpResponse
from django.template import loader

import config
import text
import dashboard.template_funcs

from data import (
    ckan,
    ckan_publishers,
    codelist_mapping,
    codelist_sets,
    codelist_lookup,
    current_stats,
    dataset_to_publisher_dict,
    github_issues,
    get_publisher_stats,
    MAJOR_VERSIONS,
    metadata,
    publisher_name,
    publishers_ordered_by_title,
    is_valid_element,
    slugs)


COMMIT_HASH = subprocess.run('git show --format=%H --no-patch'.split(),
                             cwd=config.join_base_path(""),
                             capture_output=True).stdout.decode().strip()
STATS_COMMIT_HASH = subprocess.run('git -C stats-calculated show --format=%H --no-patch'.split(),
                                   cwd=config.join_base_path(""),
                                   capture_output=True).stdout.decode().strip()
STATS_GH_URL = 'https://github.com/codeforIATI/IATI-Stats-public/tree/' + STATS_COMMIT_HASH


def _make_context(page_name: str):
    """Make a basic context dictionary for a given page
    """
    context = dict(
        page=page_name,
        top_titles=text.top_titles,
        page_titles=text.page_titles,
        short_page_titles=text.short_page_titles,
        page_leads=text.page_leads,
        page_sub_leads=text.page_sub_leads,
        top_navigation=text.top_navigation,
        navigation=text.navigation,
        navigation_reverse={page: k for k, pages in text.navigation.items() for page in pages},
        page_view_names={"index": "dash-index",
                         "headlines": "dash-headlines",
                         "data_quality": "dash-dataquality",
                         "publishing_stats": "dash-publishingstats",
                         "exploring_data": "dash-exploringdata",
                         "faq": "dash-faq",

                         "publishers": "dash-headlines-publishers",
                         "files": "dash-headlines-files",
                         "activities": "dash-headlines-activities",
                         "publisher": "dash-headlines-publisher-detail",

                         "download": "dash-dataquality-download",
                         "xml": "dash-dataquality-xml",
                         "validation": "dash-dataquality-validation",
                         "versions": "dash-dataquality-versions",
                         "organisation": "dash-dataquality-organisation",
                         "licenses": "dash-dataquality-licenses",
                         "identifiers": "dash-dataquality-identifiers",
                         "reporting_orgs": "dash-dataquality-reportingorgs",

                         "elements": "dash-exploringdata-elements",
                         "codelists": "dash-exploringdata-codelists",
                         "booleans": "dash-exploringdata-booleans",
                         "dates": "dash-exploringdata-dates",
                         "traceability": "dash-exploringdata-traceability",
                         "org_ids": "dash-exploringdata-orgids",

                         "timeliness": "dash-publishingstats-timeliness",
                         "forwardlooking": "dash-publishingstats-forwardlooking",
                         "comprehensiveness": "dash-publishingstats-comprehensiveness",
                         "coverage": "dash-publishingstats-coverage",
                         "summary_stats": "dash-publishingstats-summarystats",
                         "humanitarian": "dash-publishingstats-humanitarian"
                         },
        current_stats=current_stats,
        publisher_name=publisher_name,
        publishers_ordered_by_title=publishers_ordered_by_title,
        ckan_publishers=ckan_publishers,
        ckan=ckan,
        codelist_lookup=codelist_lookup,
        codelist_mapping=codelist_mapping,
        codelist_sets=codelist_sets,
        github_issues=github_issues,
        MAJOR_VERSIONS=MAJOR_VERSIONS,
        metadata=metadata,
        slugs=slugs,
        datetime_data=dateutil.parser.parse(metadata['created_at']).strftime('%-d %B %Y (at %H:%M %Z)'),
        stats_url='https://stats.codeforiati.org',
        stats_gh_url=STATS_GH_URL,
        commit_hash=COMMIT_HASH,
        stats_commit_hash=STATS_COMMIT_HASH,
        func={"sorted": sorted,
              "firstint": dashboard.template_funcs.firstint,
              "dataset_to_publisher": lambda x: dataset_to_publisher_dict.get(x, ""),
              "get_publisher_stats": get_publisher_stats,
              "is_valid_element": is_valid_element}
    )
    context["navigation_reverse"].update({k: k for k in text.navigation})

    return context


#
# Top level navigation pages.
#
def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render(_make_context("index"), request))


def headlines(request):
    template = loader.get_template("headlines.html")
    return HttpResponse(template.render(_make_context("headlines"), request))


def data_quality(request):
    template = loader.get_template("data_quality.html")
    return HttpResponse(template.render(_make_context("data_quality"), request))


def publishing_stats(request):
    template = loader.get_template("publishing_stats.html")
    return HttpResponse(template.render(_make_context("publishing_stats"), request))


def exploring_data(request):
    template = loader.get_template("exploring_data.html")
    return HttpResponse(template.render(_make_context("exploring_data"), request))


def faq(request):
    template = loader.get_template("faq.html")
    return HttpResponse(template.render(_make_context("faq"), request))


#
# Headline pages.
#
def headlines_publishers(request):
    template = loader.get_template("publishers.html")
    return HttpResponse(template.render(_make_context("publishers"), request))


def headlines_activities(request):
    template = loader.get_template("activities.html")
    return HttpResponse(template.render(_make_context("activities"), request))


def headlines_files(request):
    template = loader.get_template("files.html")
    return HttpResponse(template.render(_make_context("files"), request))


def headlines_publisher_detail(request, publisher=None):
    # Not implemented yet.
    return None
