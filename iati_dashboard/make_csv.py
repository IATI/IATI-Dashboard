"""Generates CSV files from data in the 'stats-calculated' folder and using additional logic"""

import csv
import logging
import os
import sys

from . import comprehensiveness, data, filepaths, forwardlooking, models, summary_stats, timeliness
from .ui.jinja2 import round_nicely

logger = logging.getLogger(__name__)


def publisher_dicts():
    publisher_name = {
        publisher: publisher_json["result"]["title"] for publisher, publisher_json in data.ckan_publishers.items()
    }
    for publisher, activities in data.current_stats["inverted_publisher"]["activities"].items():
        if publisher not in data.ckan_publishers:
            continue
        publisher_stats = data.get_publisher_stats(publisher)
        yield {
            "Publisher Name": publisher_name[publisher],
            "Publisher Registry Id": publisher,
            "Activities": activities,
            "Organisations": publisher_stats["organisations"],
            "Files": publisher_stats["activity_files"] + publisher_stats["organisation_files"],
            "Activity Files": publisher_stats["activity_files"],
            "Organisation Files": publisher_stats["organisation_files"],
            "Total File Size": publisher_stats["file_size"],
            "Reporting Org on Registry": data.ckan_publishers[publisher]["result"]["publisher_iati_id"],
            "Reporting Orgs in Data (count)": len(publisher_stats["reporting_orgs"]),
            "Reporting Orgs in Data": ";".join(publisher_stats["reporting_orgs"]),
            "Hierarchies (count)": len(publisher_stats["hierarchies"]),
            "Hierarchies": ";".join(publisher_stats["hierarchies"]),
        }


def make_csv(verbose=False):
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logger.info("Generating CSV files")
    os.makedirs(filepaths.join_out_path("data/csv"), exist_ok=True)

    logger.info("Generating publishers.csv")
    with open(filepaths.join_out_path("data/csv/publishers.csv"), "w") as fp:
        writer = csv.DictWriter(
            fp,
            [
                "Publisher Name",
                "Publisher Registry Id",
                "Activities",
                "Organisations",
                "Files",
                "Activity Files",
                "Organisation Files",
                "Total File Size",
                "Reporting Org on Registry",
                "Reporting Orgs in Data (count)",
                "Reporting Orgs in Data",
                "Hierarchies (count)",
                "Hierarchies",
            ],
        )
        writer.writeheader()
        for d in publisher_dicts():
            writer.writerow(d)

    logger.info("Generating elements.csv")
    publishers = list(data.current_stats["inverted_publisher"]["activities"].keys())
    with open(filepaths.join_out_path("data/csv/elements.csv"), "w") as fp:
        writer = csv.DictWriter(fp, ["Element"] + publishers)
        writer.writeheader()
        for element, publisher_dict in data.current_stats["inverted_publisher"]["elements"].items():
            publisher_dict["Element"] = element
            writer.writerow(publisher_dict)

    logger.info("Generating elements_total.csv")
    with open(filepaths.join_out_path("data/csv/elements_total.csv"), "w") as fp:
        writer = csv.DictWriter(fp, ["Element"] + publishers)
        writer.writeheader()
        for element, publisher_dict in data.current_stats["inverted_publisher"]["elements_total"].items():
            publisher_dict["Element"] = element
            writer.writerow(publisher_dict)

    publishers = models.ReportingOrg.objects.all().order_by("human_readable_name")

    logger.info("Generating timeliness_frequency.csv")
    previous_months = timeliness.previous_months_reversed
    with open(filepaths.join_out_path("data/csv/timeliness_frequency.csv"), "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(
            ["Publisher Name", "Publisher Registry Id"] + previous_months + ["Frequency", "First published"]
        )
        for publisher in publishers:
            per_month = publisher.timeliness_frequency["updates_per_month"]
            first_published_band = publisher.timeliness_frequency["first_published_band"]
            assessment = publisher.timeliness_frequency["frequency"]
            # hft=publisher.has_future_transactions
            writer.writerow(
                [publisher.human_readable_name, publisher.short_name]
                + [per_month.get(x) or 0 for x in previous_months]
                + [assessment, first_published_band]
            )

    logger.info("Generating timeliness_timelag.csv")
    with open(filepaths.join_out_path("data/csv/timeliness_timelag.csv"), "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(["Publisher Name", "Publisher Registry Id"] + previous_months + ["Time lag"])
        for publisher in publishers:
            per_month = publisher.stats_json["transaction_months_with_year"]
            # hft=publisher.has_future_transactions
            previous_months = timeliness.previous_months_reversed
            assessment = publisher.stats_json["timelag"]
            writer.writerow(
                [publisher.human_readable_name, publisher.short_name]
                + [per_month.get(x) or 0 for x in previous_months]
                + [assessment]
            )

    logger.info("Generating forwardlooking.csv")
    with open(filepaths.join_out_path("data/csv/forwardlooking.csv"), "w") as fp:
        writer = csv.writer(fp)
        writer.writerow(
            ["Publisher Name", "Publisher Registry Id"]
            + [
                "{} ({})".format(header, year)
                for header in forwardlooking.column_headers
                for year in forwardlooking.years
            ]
        )
        for row in forwardlooking.table():
            writer.writerow(
                [row["publisher_title"], row["publisher"]]
                + [
                    round_nicely(year_column[year])
                    for year_column in row["year_columns"]
                    for year in forwardlooking.years
                ]
            )

    for tab in comprehensiveness.columns.keys():
        logger.info("Generating comprehensiveness_{}.csv".format(tab))
        with open(filepaths.join_out_path("data/csv/comprehensiveness_{}.csv".format(tab)), "w") as fp:
            writer = csv.writer(fp)
            if tab == "financials":
                writer.writerow(
                    ["Publisher Name", "Publisher Registry Id"]
                    + [x + " (with valid data)" for x in comprehensiveness.column_headers[tab]]
                    + [x + " (with any data)" for x in comprehensiveness.column_headers[tab]]
                    + ["Using budget-not-provided"]
                )
                for row in comprehensiveness.table():
                    writer.writerow(
                        [row["publisher_title"], row["publisher"]]
                        + [
                            round_nicely(row[slug + "_valid"]) if slug in row else "-"
                            for slug in comprehensiveness.column_slugs[tab]
                        ]
                        + [
                            round_nicely(row[slug]) if slug in row else "-"
                            for slug in comprehensiveness.column_slugs[tab]
                        ]
                        + ["Yes" if row["flag"] else "-"]
                    )
            else:
                writer.writerow(
                    ["Publisher Name", "Publisher Registry Id"]
                    + [x + " (with valid data)" for x in comprehensiveness.column_headers[tab]]
                    + [x + " (with any data)" for x in comprehensiveness.column_headers[tab]]
                )
                for row in comprehensiveness.table():
                    writer.writerow(
                        [row["publisher_title"], row["publisher"]]
                        + [
                            round_nicely(row[slug + "_valid"]) if slug in row else "-"
                            for slug in comprehensiveness.column_slugs[tab]
                        ]
                        + [
                            round_nicely(row[slug]) if slug in row else "-"
                            for slug in comprehensiveness.column_slugs[tab]
                        ]
                    )

    logger.info("Generating summary_stats.csv")
    with open(filepaths.join_out_path("data/csv/summary_stats.csv"), "w") as fp:
        writer = csv.writer(fp)
        # Add column headers
        writer.writerow(
            ["Publisher Name", "Publisher Registry Id"] + [header for slug, header in summary_stats.columns]
        )
        for publisher in publishers:
            # Write each row
            if publisher.summary_stats:
                writer.writerow(
                    [publisher.human_readable_name, publisher.short_name]
                    + [
                        (
                            publisher.summary_stats[column_slug]
                            if header == "Reporting Org Type"
                            else round_nicely(publisher.summary_stats[column_slug])
                        )
                        for column_slug, header in summary_stats.columns
                    ]
                )

    logger.info("Generating humanitarian.csv")
    with open(filepaths.join_out_path("data/csv/humanitarian.csv"), "w") as fp:
        writer = csv.writer(fp)
        # Add column headers
        writer.writerow(
            [
                "Publisher Name",
                "Publisher Registry Id",
                "Publisher Type",
                "Number of Activities",
                "Publishing Humanitarian",
                "Using Humanitarian Attribute",
                "Appeal or Emergency Details",
                "Clusters",
                "Humanitarian Score",
            ]
        )
        for publisher in publishers:
            row = publisher.humanitarian
            if row:
                writer.writerow(
                    [
                        publisher.human_readable_name,
                        publisher.short_name,
                        row["publisher_type"],
                        row["num_activities"],
                        round_nicely(row["publishing_humanitarian"]),
                        round_nicely(row["humanitarian_attrib"]),
                        round_nicely(row["appeal_emergency"]),
                        round_nicely(row["clusters"]),
                        round_nicely(row["average"]),
                    ]
                )
