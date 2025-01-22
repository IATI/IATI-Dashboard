# This file converts a range of transparency data to percentages

from . import common
from .data import secondary_publishers
from .ui.jinja2 import round_nicely

# Set column groupings, to be displayed in the user output
columns = [
    # slug, header
    ("publisher_type", "Publisher Type"),
    ("timeliness", "Timeliness"),
    ("forwardlooking", "Forward looking"),
    ("comprehensiveness", "Comprehensiveness"),
    ("score", "Score"),
]


def is_number(s):
    """@todo Document this function"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def convert_to_float(x):
    """@todo Document this function"""
    if is_number(x):
        return float(x)
    else:
        return 0


def generate_row(publisher):
    """Generate data for the publisher forward-looking table"""

    # Skip if all activities from this publisher are secondary reported
    if publisher.short_name in secondary_publishers:
        return {}

    # Create a list for publisher data, and populate it with basic data
    row = {}
    row["publisher"] = publisher.short_name
    row["publisher_type"] = common.get_publisher_type(publisher.short_name)["name"]

    # Compute timeliness statistic
    # Assign frequency score
    # Get initial frequency assessment, or use empty set in the case where the publisher is not found
    frequency_assessment_data = publisher.timeliness_frequency
    frequency_assessment = None if len(frequency_assessment_data) < 4 else frequency_assessment_data[3]
    if frequency_assessment == "Monthly":
        frequency_score = 4
    elif frequency_assessment == "Quarterly":
        frequency_score = 3
    elif frequency_assessment == "Six-Monthly":
        frequency_score = 2
    elif frequency_assessment == "Annual":
        frequency_score = 1
    else:  # frequency_assessment == 'Less than Annual' or something else!
        frequency_score = 0

    # Assign timelag score
    # Get initial timelag assessment, or use empty set in the case where the publisher is not found
    timelag_assessment = publisher.stats_json["timelag"]
    if timelag_assessment == "One month":
        timelag_score = 4
    elif timelag_assessment == "A quarter":
        timelag_score = 3
    elif timelag_assessment == "Six months":
        timelag_score = 2
    elif timelag_assessment == "One year":
        timelag_score = 1
    else:  # timelag_assessment == 'More than one year' or something else!
        timelag_score = 0

    # Compute the percentage
    row["timeliness"] = round_nicely((float(frequency_score + timelag_score) / 8) * 100)

    # Compute forward-looking statistic
    # Get the forward-looking data for this publisher
    publisher_forwardlooking_data = publisher.forwardlooking

    # Convert the data for this publishers 'Percentage of current activities with budgets' fields into integers
    numbers = [int(x) for x in publisher_forwardlooking_data["year_columns"][2].values() if is_number(x)]

    # Compute and store the mean average for these fields
    row["forwardlooking"] = round_nicely(
        sum(int(round(y)) for y in numbers) / len(publisher_forwardlooking_data["year_columns"][2])
    )

    # Compute comprehensiveness statistic
    # Get the comprehensiveness data for this publisher
    publisher_comprehensiveness_data = publisher.comprehensiveness

    # Set the comprehensiveness value to be the summary average for valid data
    row["comprehensiveness"] = convert_to_float(publisher_comprehensiveness_data["summary_average_valid"])

    # Compute score
    row["score"] = round_nicely(float(row["timeliness"] + row["forwardlooking"] + row["comprehensiveness"]) / 3)

    return row
