# This file builds a table to show humanitarian reporting for each publisher

from .common import get_publisher_type
from .data import get_publisher_stats

# Set column groupings, to be displayed in the user output
columns = [
    # slug, header
    ("publisher_type", "Reporting Org Type"),
    ("num_activities", "Number of Activities"),
    ("publishing_humanitarian", "Publishing Humanitarian?"),
    ("humanitarian_attrib", "Using Humanitarian Attribute?"),
    ("appeal_emergency", "Appeal or Emergency Details"),
    ("clusters", "Clusters"),
    ("average", "Average"),
]


def generate_row(publisher):
    """Generate data for the humanitarian table"""

    publisher_stats = get_publisher_stats(publisher)

    # Create a list for publisher data, and populate it with basic data
    row = {}
    row["publisher"] = publisher
    row["publisher_type"] = get_publisher_type(publisher)["name"]

    # Get data from IATI-Stats output
    row["num_activities"] = publisher_stats.get("humanitarian", {}).get("is_humanitarian", "0")
    row["publishing_humanitarian"] = 100 if int(row["num_activities"]) > 0 else 0

    # Calculate percentage of all humanitarian activities that are defined using the @humanitarian attribute
    row["humanitarian_attrib"] = (
        publisher_stats.get("humanitarian", {}).get("is_humanitarian_by_attrib", "0") / float(row["num_activities"])
        if int(row["num_activities"]) > 0
        else 0.0
    ) * 100

    # Calculate percentage of all humanitarian activities that use the <humanitarian-scope> element to define an appeal or emergency
    row["appeal_emergency"] = (
        publisher_stats.get("humanitarian", {}).get("contains_humanitarian_scope", "0") / float(row["num_activities"])
        if int(row["num_activities"]) > 0
        else 0.0
    ) * 100

    # Calculate percentage of all humanitarian activities that use clusters
    row["clusters"] = (
        publisher_stats.get("humanitarian", {}).get("uses_humanitarian_clusters_vocab", "0")
        / float(row["num_activities"])
        if int(row["num_activities"]) > 0
        else 0.0
    ) * 100

    # Calculate the mean average
    row["average"] = (
        row["publishing_humanitarian"] + row["humanitarian_attrib"] + row["appeal_emergency"] + row["clusters"]
    ) / float(4)

    return row
