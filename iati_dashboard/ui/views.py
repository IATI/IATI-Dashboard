"""Views for the IATI Dashboard"""

import collections
import csv
import datetime
import json
import subprocess

import dateutil.parser
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import Http404, HttpResponse
from django.template import loader

from .. import (
    activity_streams,
    comprehensiveness,
    filepaths,
    filters,
    forwardlooking,
    humanitarian,
    models,
    summary_stats,
    text,
    timeliness,
    vars,
)
from ..data import (
    MAJOR_VERSIONS,
    codelist_lookup,
    codelist_mapping,
    codelist_sets,
    current_stats,
    element_slug,
    get_publisher_stats,
    is_valid_element_or_attribute,
    metadata_datasets,
    publisher_name,
    publishers_ordered_by_title,
    slugs,
)
from . import template_funcs

COMMIT_HASH = (
    subprocess.run("git show --format=%H --no-patch".split(), cwd=filepaths.join_base_path(""), capture_output=True)
    .stdout.decode()
    .strip()
)
STATS_COMMIT_HASH = (
    subprocess.run(
        "git -C stats-calculated show --format=%H --no-patch".split(),
        cwd=filepaths.join_base_path(""),
        capture_output=True,
    )
    .stdout.decode()
    .strip()
)

ACTIVITY_STREAM_HISTORY_PAGE_SIZE = 25

# Load all the licenses and generate data for each licence and publisher.
with open(filepaths.join_stats_path("licenses.json")) as handler:
    LICENSE_URLS = json.load(handler)

LICENSES = [
    dataset["licence_id"] if dataset["licence_id"] else "notspecified" for dataset in metadata_datasets["datasets"]
]

LICENCE_COUNT = dict((x, LICENSES.count(x)) for x in set(LICENSES))

LICENSES_AND_PUBLISHER = set(
    [
        (
            dataset["licence_id"] if dataset["licence_id"] else "notspecified",
            dataset["reporting_org_short_name"],
        )
        for dataset in metadata_datasets["datasets"]
    ]
)

LICENSES_PER_PUBLISHER = [license for license, publisher in LICENSES_AND_PUBLISHER]
PUBLISHER_LICENSE_COUNT = dict((x, LICENSES_PER_PUBLISHER.count(x)) for x in set(LICENSES_PER_PUBLISHER))


def _get_licenses_for_publisher(short_name):
    # Check publisher is in the compiled list of CKAN data
    # Arises from https://github.com/IATI/IATI-Dashboard/issues/408

    # Return unique licenses used
    return set(
        [
            (dataset.metadata_json["licence_id"] if dataset.metadata_json.get("licence_id") else "notspecified")
            for dataset in models.ReportingOrg.objects.get(short_name=short_name).dataset_set.all()
        ]
    )


def _registration_agency(orgid):
    for code in codelist_sets["2"]["OrganisationRegistrationAgency"]:
        if orgid.startswith(code):
            return code


def dictinvert(d):
    inv = collections.defaultdict(list)
    for k, v in d.items():
        inv[v].append(k)
    return inv


def nested_dictinvert(d):
    inv = collections.defaultdict(lambda: collections.defaultdict(int))
    for k, v in d.items():
        for k2, v2 in v.items():
            inv[k2][k] += v2
    return inv


PAGE_VIEW_NAMES = {
    "index": "dash-index",
    "headlines": "dash-headlines",
    "errors": "dash-errors",
    "publishing_stats": "dash-publishingstats",
    "exploring_data": "dash-exploringdata",
    "faq": "dash-faq",
    "publishers": "dash-headlines-publishers",
    "files": "dash-headlines-datasets",
    "activities": "dash-headlines-activities",
    "publisher": "dash-headlines-publisher-detail",
    "dataset": "dash-headlines-dataset-detail",
    "download": "dash-errors-download",
    "xml": "dash-errors-xml",
    "validation": "dash-errors-validation",
    "versions": "dash-versions",
    "organisation": "dash-organisation",
    "licenses": "dash-licenses",
    "identifiers": "dash-identifiers",
    "reporting_orgs": "dash-errors-reportingorgs",
    "elements": "dash-exploringdata-elements",
    "codelists": "dash-exploringdata-codelists",
    "booleans": "dash-exploringdata-booleans",
    "dates": "dash-exploringdata-dates",
    "traceability": "dash-exploringdata-traceability",
    "org_ids": "dash-exploringdata-orgids",
    "timeliness_timelag": "dash-publishingstats-timeliness-timelag",
    "timeliness_frequency": "dash-publishingstats-timeliness-frequency",
    "forwardlooking": "dash-publishingstats-forwardlooking",
    "comprehensiveness_summary": "dash-publishingstats-comprehensiveness-summary",
    "comprehensiveness_core": "dash-publishingstats-comprehensiveness-core",
    "comprehensiveness_financials": "dash-publishingstats-comprehensiveness-financials",
    "comprehensiveness_valueadded": "dash-publishingstats-comprehensiveness-valueadded",
    "coverage": "dash-publishingstats-coverage",
    "summary_stats": "dash-publishingstats-summarystats",
    "humanitarian": "dash-publishingstats-humanitarian",
}


metadata_datasets_dict = {d["short_name"]: d for d in metadata_datasets["datasets"]}


def dataset_to_publisher(dataset_short_name):
    return metadata_datasets_dict.get(dataset_short_name, {}).get("reporting_org_short_name")


def _make_context(page_name: str, include_large_dicts: bool = True):
    """Make a basic context dictionary for a given page"""

    with open(filepaths.join_stats_path("gitdate.json")) as fp:
        date_time_data_str = max(json.load(fp).values())
    date_time_data_obj = dateutil.parser.parse(date_time_data_str)

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
        page_view_names=PAGE_VIEW_NAMES,
        publisher_name=publisher_name,
        publishers_ordered_by_title=publishers_ordered_by_title,
        publishers=models.ReportingOrg.objects.all().order_by("human_readable_name").defer("stats_json"),
        MAJOR_VERSIONS=MAJOR_VERSIONS,
        expected_versions=vars.expected_versions,
        slugs=slugs,
        datetime_data=date_time_data_obj.strftime("%-d %B %Y (at %H:%M %Z)"),
        current_year=datetime.datetime.now(datetime.UTC).year,
        stats_url="/stats",
        generated_url="/generated",
        commit_hash=COMMIT_HASH,
        stats_commit_hash=STATS_COMMIT_HASH,
        func={
            "sorted": sorted,
            "firstint": template_funcs.firstint,
            "get_codelist_values": template_funcs.get_codelist_values,
            "dataset_to_publisher": dataset_to_publisher,
            "get_publisher_stats": get_publisher_stats,
            "is_valid_element_or_attribute": is_valid_element_or_attribute,
            "set": set,
            "enumerate": enumerate,
        },
        breadcrumbs=[{"view": "dash-index", "title": "Home"}],
        element_slug=element_slug,
    )

    context["navigation_reverse"].update({k: k for k in text.navigation})

    # Build the list of breadcrumbs for page navigation rather than doing
    # it programmatically in the template.
    if page_name == "index":
        pass
    elif page_name == "registration_agencies":
        context["breadcrumbs"].append({"view": "dash-registrationagencies", "title": "Registration Agencies"})
    else:
        if page_name in text.top_titles:
            context["breadcrumbs"].append({"view": PAGE_VIEW_NAMES[page_name], "title": text.top_titles[page_name]})
        else:
            context["breadcrumbs"].append(
                {
                    "view": PAGE_VIEW_NAMES[context["navigation_reverse"][page_name]],
                    "title": text.top_titles[context["navigation_reverse"][page_name]],
                }
            )
            context["breadcrumbs"].append(
                {"view": PAGE_VIEW_NAMES[page_name], "title": text.short_page_titles[page_name]}
            )

    if include_large_dicts:
        # Have the option to exclude these dicts, as they slow the debug pages down consiberably
        context["current_stats"] = current_stats
    context["codelist_lookup"] = codelist_lookup
    context["codelist_mapping"] = codelist_mapping
    context["codelist_sets"] = codelist_sets

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


def errors(request):
    template = loader.get_template("errors.html")
    return HttpResponse(template.render(_make_context("errors"), request))


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
    context = _make_context("publishers", include_large_dicts=False)
    context["filter"] = filters.ReportingOrgFilter(request.GET, queryset=models.ReportingOrg.objects.all())
    context["show_filters"] = settings.ENABLE_FILTERS_ALPHA
    template = loader.get_template("publishers.html")
    return HttpResponse(template.render(context, request))


def headlines_activities(request):
    template = loader.get_template("activities.html")
    return HttpResponse(template.render(_make_context("activities"), request))


def headlines_publisher_detail(request, publisher_short_name=None):
    try:
        publisher = models.ReportingOrg.objects.get(short_name=publisher_short_name)
    except models.ReportingOrg.DoesNotExist:
        raise Http404("Publisher does not exist")

    template = loader.get_template("publisher.html")

    context = _make_context("publishers", include_large_dicts=False)
    context["breadcrumbs"].append({"view": PAGE_VIEW_NAMES["publisher"], "title": publisher.human_readable_name})
    context["publisher"] = publisher
    context["publisher_licenses"] = _get_licenses_for_publisher(publisher_short_name)

    try:
        context["budget_table"] = [
            {
                "year": "Total",
                "count_total": sum(
                    sum(x.values()) for x in publisher.stats_json["count_budgets_by_type_by_year"].values()
                ),
                "sum_total": {
                    currency: sum(sums.values())
                    for by_currency in publisher.stats_json["sum_budgets_by_type_by_year"].values()
                    for currency, sums in by_currency.items()
                },
                "count_original": (
                    sum(publisher.stats_json["count_budgets_by_type_by_year"]["1"].values())
                    if "1" in publisher.stats_json["count_budgets_by_type_by_year"]
                    else None
                ),
                "sum_original": (
                    {k: sum(v.values()) for k, v in publisher.stats_json["sum_budgets_by_type_by_year"]["1"].items()}
                    if "1" in publisher.stats_json["sum_budgets_by_type_by_year"]
                    else None
                ),
                "count_revised": (
                    sum(publisher.stats_json["count_budgets_by_type_by_year"]["2"].values())
                    if "2" in publisher.stats_json["count_budgets_by_type_by_year"]
                    else None
                ),
                "sum_revised": (
                    {k: sum(v.values()) for k, v in publisher.stats_json["sum_budgets_by_type_by_year"]["2"].items()}
                    if "2" in publisher.stats_json["sum_budgets_by_type_by_year"]
                    else None
                ),
            }
        ] + [
            {
                "year": year,
                "count_total": sum(
                    x[year] for x in publisher.stats_json["count_budgets_by_type_by_year"].values() if year in x
                ),
                "sum_total": {
                    currency: sums.get(year)
                    for by_currency in publisher.stats_json["sum_budgets_by_type_by_year"].values()
                    for currency, sums in by_currency.items()
                },
                "count_original": (
                    publisher.stats_json["count_budgets_by_type_by_year"]["1"].get(year)
                    if "1" in publisher.stats_json["count_budgets_by_type_by_year"]
                    else None
                ),
                "sum_original": (
                    {k: v.get(year) for k, v in publisher.stats_json["sum_budgets_by_type_by_year"]["1"].items()}
                    if "1" in publisher.stats_json["sum_budgets_by_type_by_year"]
                    else None
                ),
                "count_revised": (
                    publisher.stats_json["count_budgets_by_type_by_year"]["2"].get(year)
                    if "2" in publisher.stats_json["count_budgets_by_type_by_year"]
                    else None
                ),
                "sum_revised": (
                    {k: v.get(year) for k, v in publisher.stats_json["sum_budgets_by_type_by_year"]["2"].items()}
                    if "2" in publisher.stats_json["sum_budgets_by_type_by_year"]
                    else None
                ),
            }
            for year in sorted(
                set(sum((list(x.keys()) for x in publisher.stats_json["count_budgets_by_type_by_year"].values()), []))
            )
        ]
    except KeyError:
        raise Http404("Publisher does not exist")

    return HttpResponse(template.render(context, request))


def headlines_datasets(request):
    datasets = models.Dataset.objects.select_related("reporting_org").only(
        "id",
        "short_name",
        "source_url",
        "activities",
        "organisations",
        "file_size",
        "reporting_org_id",
        "reporting_org__short_name",
        "reporting_org__human_readable_name",
    )
    context = _make_context("files")
    context["datasets"] = datasets
    template = loader.get_template("files.html")
    return HttpResponse(template.render(context, request))


def debug(request):
    datasets = (
        models.Dataset.objects.select_related("reporting_org").only(
            "id",
            "short_name",
            "source_url",
            "activities",
            "organisations",
            "file_size",
            "metadata_json_datetime",
            "check_result_json_datetime",
            "reporting_org_id",
            "reporting_org__short_name",
            "reporting_org__human_readable_name",
        )
    ).order_by("-metadata_json_datetime")
    context = {}
    context["datasets"] = datasets
    template = loader.get_template("debug.html")
    return HttpResponse(template.render(context, request))


def headlines_dataset_detail(request, dataset_short_name: str | None = None) -> HttpResponse:
    try:
        dataset: models.Dataset = (
            models.Dataset.objects.select_related("reporting_org")
            .only(
                "id",
                "short_name",
                "source_url",
                "metadata_json",
                "stats_json",
                "reporting_org_id",
                "reporting_org__short_name",
                "reporting_org__human_readable_name",
                "reporting_org__organisation_identifier",
            )
            .get(short_name=dataset_short_name)
        )
    except models.Dataset.DoesNotExist:
        raise Http404("Dataset does not exist")

    dataset_history_qs = (
        models.DatasetHistoricEvent.objects.using("activity_stream")
        .filter(dataset_id=dataset.id)
        .filter(Q(display_category__isnull=True) | ~Q(display_category="CONTENT_CHANGED_ANY"))
        .order_by("-message_date", "-id")
    )

    paginator = Paginator(dataset_history_qs, ACTIVITY_STREAM_HISTORY_PAGE_SIZE)

    history_page = paginator.get_page(request.GET.get("page", 1))

    paged_dataset_history_entries = [
        {
            "message_date": item.message_date,
            "message_type": item.message_type,
            **activity_streams.render_message_type_for_payload(item.message_type, item.display_category, item.payload),
        }
        for item in history_page.object_list
        if activity_streams.message_type_has_handler(item.message_type, item.display_category)
    ]

    template = loader.get_template("dataset.html")

    context = _make_context("publishers")
    context["breadcrumbs"].append(  # type: ignore
        {
            "view": PAGE_VIEW_NAMES["publisher"],
            "view_arg": dataset.reporting_org.short_name,
            "title": dataset.reporting_org.human_readable_name,
        }  # type: ignore
    )
    context["breadcrumbs"].append({"view": PAGE_VIEW_NAMES["dataset"], "title": dataset.short_name})  # type: ignore
    context["dataset"] = dataset  # type: ignore
    context["dataset_change_history"] = paged_dataset_history_entries  # type: ignore
    context["history_page"] = history_page  # type: ignore

    return HttpResponse(template.render(context, request))


#
# Views to generate data quality pages.
#
def _datasets_with_errors():
    return (
        models.Dataset.objects.exclude(metadata_json__most_recent_get_attempt__error_details__error_type=None)
        .select_related("reporting_org")
        .annotate(
            error_type=F("metadata_json__most_recent_get_attempt__error_details__error_type"),
            http_status=F("metadata_json__most_recent_get_attempt__error_details__http_status"),
        )
        .order_by("reporting_org__human_readable_name")
        .defer("stats_json", "metadata_json", "reporting_org__stats_json", "reporting_org__metadata_json")
    )


def errors_download(request):
    template = loader.get_template("download.html")
    context = _make_context("download", include_large_dicts=False)
    context["datasets_with_errors"] = _datasets_with_errors()
    return HttpResponse(template.render(context, request))


def errors_download_csv(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="download-errors.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "Reporting Org Human Readable Name",
            "Reporting Org Short Name",
            "Dataset Short Name",
            "URL",
            "Error Type",
            "HTTP Status",
        ]
    )
    for dataset in _datasets_with_errors():
        writer.writerow(
            [
                dataset.reporting_org.human_readable_name,
                dataset.reporting_org.short_name,
                dataset.short_name,
                dataset.source_url,
                dataset.error_type,
                dataset.http_status,
            ]
        )

    return response


def errors_xml(request):
    template = loader.get_template("xml.html")
    context = _make_context("xml")
    return HttpResponse(template.render(context, request))


def errors_validation(request):
    template = loader.get_template("validation.html")
    context = _make_context("validation")
    return HttpResponse(template.render(context, request))


def versions(request):
    template = loader.get_template("versions.html")
    context = _make_context("versions")
    return HttpResponse(template.render(context, request))


def licenses(request):
    template = loader.get_template("licenses.html")
    context = _make_context("licenses")
    context["license_urls"] = LICENSE_URLS
    context["license_names"] = text.LICENSE_NAMES
    context["licenses"] = True
    context["license_count"] = LICENCE_COUNT
    context["publisher_license_count"] = PUBLISHER_LICENSE_COUNT
    return HttpResponse(template.render(context, request))


def licenses_detail(request, license_id=None):
    template = loader.get_template("license.html")

    if license_id not in LICENSE_URLS:
        raise Http404("Unknown license")

    if license_id == "notspecified":
        filters = (
            Q(dataset__metadata_json__licence_id=license_id)
            | Q(dataset__metadata_json__licence_id="")
            | Q(dataset__metadata_json__licence_id=None)
        )
    else:
        filters = Q(dataset__metadata_json__licence_id=license_id)
    reporting_orgs = models.ReportingOrg.objects.filter(filters).annotate(Count("dataset"))
    context = _make_context("licenses")
    context["breadcrumbs"].append({"view": PAGE_VIEW_NAMES["licenses"], "title": text.LICENSE_NAMES[license_id]})
    context["license_urls"] = LICENSE_URLS
    context["license_names"] = text.LICENSE_NAMES
    context["licenses"] = True
    context["license"] = license_id
    context["publisher_counts"] = [
        (reporting_org.short_name, reporting_org.dataset_count) for reporting_org in reporting_orgs
    ]
    return HttpResponse(template.render(context, request))


def orgxml(request):
    template = loader.get_template("organisation.html")
    context = _make_context("organisation")
    return HttpResponse(template.render(context, request))


def errors_identifiers(request):
    template = loader.get_template("identifiers.html")
    context = _make_context("identifiers")
    return HttpResponse(template.render(context, request))


def errors_reportingorgs(request):
    template = loader.get_template("reporting_orgs.html")
    context = _make_context("reporting_orgs")
    return HttpResponse(template.render(context, request))


#
# Exploring data pages.
#
def exploringdata_elements(request):
    template = loader.get_template("elements.html")
    return HttpResponse(template.render(_make_context("elements"), request))


def exploringdata_element_detail(request, element=None):
    template = loader.get_template("element.html")
    context = _make_context("elements", include_large_dicts=False)

    context["element"] = element.replace("_", "/").replace("xml:", "{http://www.w3.org/XML/1998/namespace}")

    values = [
        "id",
        "short_name",
        "activities",
        "organisations",
        "activity_files",
        "organisation_files",
        "elements",
        "elements_total",
    ]
    context["publishers_with"] = models.ReportingOrg.objects.filter(elements__has_key=context["element"]).values(
        *values
    )
    context["publishers_without"] = models.ReportingOrg.objects.exclude(elements__has_key=context["element"]).values(
        *values
    )

    if context["publishers_with"].count() == 0:
        raise Http404("Unknown element or attribute")

    context["element_or_attribute"] = "attribute" if "@" in context["element"] else "element"

    context["breadcrumbs"].append({"view": PAGE_VIEW_NAMES["elements"], "title": '"' + context["element"] + '"'})

    return HttpResponse(template.render(context, request))


def exploringdata_orgids(request):
    template = loader.get_template("org_ids.html")
    return HttpResponse(template.render(_make_context("org_ids"), request))


def exploringdata_orgtypes_detail(request, org_type=None):
    if org_type not in slugs["org_type"]["by_slug"]:
        raise Http404("Unknown organisation type")

    template = loader.get_template("org_type.html")
    context = _make_context("org_ids")
    context["slug"] = org_type

    context["breadcrumbs"].append(
        {"view": PAGE_VIEW_NAMES["org_ids"], "title": org_type.replace("_org", "").title() + " Organisations"}
    )

    return HttpResponse(template.render(context, request))


def exploringdata_codelists(request):
    template = loader.get_template("codelists.html")
    return HttpResponse(template.render(_make_context("codelists"), request))


def _codelist_detail_context(context, major_version, codelist_mapping):
    context["reverse_codelist_mapping"] = {
        major_version: dictinvert(mapping) for major_version, mapping in codelist_mapping.items()
    }
    context["major_version"] = major_version


def exploringdata_codelists_detail(request, major_version=None, attribute=None):
    template = loader.get_template("codelist.html")

    if major_version not in slugs["codelist"]:
        raise Http404("Unknown major version of the IATI standard")
    if attribute not in slugs["codelist"][major_version]["by_slug"]:
        raise Http404("Unknown attribute")

    context = _make_context("codelists")
    i = slugs["codelist"][major_version]["by_slug"][attribute]
    element = list(current_stats["inverted_publisher"]["codelist_values_by_major_version"][major_version])[i]
    values = nested_dictinvert(
        list(current_stats["inverted_publisher"]["codelist_values_by_major_version"][major_version].values())[i]
    )
    context["element"] = element
    context["values"] = values
    _codelist_detail_context(context, major_version, codelist_mapping)

    context["breadcrumbs"].append({"view": PAGE_VIEW_NAMES["codelists"], "title": '"' + element + '"'})

    return HttpResponse(template.render(context, request))


def exploringdata_publisher_codelist_detail(request, publisher_short_name=None, major_version=None, attribute=None):
    try:
        publisher = models.ReportingOrg.objects.get(short_name=publisher_short_name)
    except models.ReportingOrg.DoesNotExist:
        raise Http404("Publisher does not exist")

    attribute = ".//" + attribute.replace("_", "/")
    if attribute.endswith("/text"):
        attribute += "()"
    values = publisher.stats_json.get("codelist_values_by_major_version", {}).get(major_version, {}).get(attribute)
    if not values:
        raise Http404("No data for that codelist")

    context = _make_context("publishers", include_large_dicts=False)
    context["publisher"] = publisher
    context["element"] = attribute
    context["values"] = values
    _codelist_detail_context(context, major_version, codelist_mapping)
    context["breadcrumbs"].append(
        {
            "view": PAGE_VIEW_NAMES["publisher"],
            "view_arg": publisher.short_name,
            "title": publisher.human_readable_name,
        }
    )
    context["breadcrumbs"].append({"title": "Codelists"})
    context["breadcrumbs"].append({"title": '"' + attribute + '"'})

    template = loader.get_template("codelist_publisher.html")
    return HttpResponse(template.render(context, request))


def exploringdata_booleans(request):
    template = loader.get_template("booleans.html")
    return HttpResponse(template.render(_make_context("booleans"), request))


def exploringdata_dates(request):
    template = loader.get_template("dates.html")
    return HttpResponse(template.render(_make_context("dates"), request))


def exploringdata_traceability(request):
    template = loader.get_template("traceability.html")
    return HttpResponse(template.render(_make_context("traceability", include_large_dicts=False), request))


#
# Publishing statistics pages.
#
def pubstats_comprehensiveness_summary(request):
    template = loader.get_template("comprehensiveness_summary.html")
    context = _make_context("comprehensiveness_summary", include_large_dicts=False)
    context["comprehensiveness"] = comprehensiveness
    return HttpResponse(template.render(context, request))


def pubstats_comprehensiveness_core(request):
    template = loader.get_template("comprehensiveness_core.html")
    context = _make_context("comprehensiveness_core", include_large_dicts=False)
    context["comprehensiveness"] = comprehensiveness
    return HttpResponse(template.render(context, request))


def pubstats_comprehensiveness_financials(request):
    template = loader.get_template("comprehensiveness_financials.html")
    context = _make_context("comprehensiveness_financials", include_large_dicts=False)
    context["comprehensiveness"] = comprehensiveness
    return HttpResponse(template.render(context, request))


def pubstats_comprehensiveness_valueadded(request):
    template = loader.get_template("comprehensiveness_valueadded.html")
    context = _make_context("comprehensiveness_valueadded", include_large_dicts=False)
    context["comprehensiveness"] = comprehensiveness
    return HttpResponse(template.render(context, request))


def pubstats_timeliness_frequency(request):
    template = loader.get_template("timeliness_frequency.html")
    context = _make_context("timeliness_frequency", include_large_dicts=False)
    context["timeliness"] = timeliness
    context["publisher_frequency_summary"] = sorted(
        list(
            models.ReportingOrg.objects.annotate(frequency=F("timeliness_frequency__frequency"))
            .values("frequency")
            .annotate(total=Count("frequency"))
        ),
        key=lambda x: timeliness.frequency_index(x["frequency"]),
    )
    context["publisher_count"] = models.ReportingOrg.objects.count()

    return HttpResponse(template.render(context, request))


def pubstats_timeliness_timelag(request):
    template = loader.get_template("timeliness_timelag.html")
    context = _make_context("timeliness_timelag", include_large_dicts=False)
    context["timeliness"] = timeliness
    context["publisher_timelag_summary"] = sorted(
        list(models.ReportingOrg.objects.values("timelag").annotate(total=Count("timelag"))),
        key=lambda x: timeliness.timelag_index(x["timelag"]),
    )
    context["publisher_count"] = models.ReportingOrg.objects.count()
    return HttpResponse(template.render(context, request))


def pubstats_summarystats(request):
    template = loader.get_template("summary_stats.html")
    context = _make_context("summary_stats", include_large_dicts=False)
    context["summary_stats"] = summary_stats
    return HttpResponse(template.render(context, request))


def pubstats_forwardlooking(request):
    template = loader.get_template("forwardlooking.html")
    context = _make_context("forwardlooking", include_large_dicts=False)
    context["forwardlooking"] = forwardlooking
    return HttpResponse(template.render(context, request))


def pubstats_humanitarian(request):
    template = loader.get_template("humanitarian.html")
    context = _make_context("humanitarian", include_large_dicts=False)
    context["humanitarian"] = humanitarian
    return HttpResponse(template.render(context, request))


#
# Registration agencies page.
#
def registration_agencies(request):
    template = loader.get_template("registration_agencies.html")

    context = _make_context("registration_agencies")
    context["registration_agencies"] = collections.defaultdict(int)
    context["registration_agencies_publishers"] = collections.defaultdict(list)
    context["nonmatching"] = []
    for orgid, publishers in current_stats["inverted_publisher"]["reporting_orgs"].items():
        reg_ag = _registration_agency(orgid)
        if reg_ag:
            context["registration_agencies"][reg_ag] += 1
            context["registration_agencies_publishers"][reg_ag] += list(publishers)
        else:
            context["nonmatching"].append((orgid, publishers))

    return HttpResponse(template.render(context, request))


#
# ATI pages
#
def ati_publishers(request):
    template = loader.get_template("ati_publishers.html")
    return HttpResponse(template.render(_make_context("ati_publishers", include_large_dicts=False), request))


def ati_publisher_detail(request, publisher):
    context = _make_context("ati_publisher_detail", include_large_dicts=False)
    context["publisher"] = publisher
    publisher_stats = get_publisher_stats(publisher)
    context["publisher_stats"] = publisher_stats

    template = loader.get_template("ati_publisher_detail.html")
    return HttpResponse(template.render(context, request))
