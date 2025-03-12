# This file converts raw timeliness data into the associated Publishing Statistics assessments

import datetime
from collections import defaultdict

from dateutil.relativedelta import relativedelta
from iati_dashboard import filepaths
from iati_dashboard.data import JSONDir, get_publisher_stats, get_registry_id_matches


def short_month(month_str):
    """Return the 'short month' represeentation of a date which is inputted as a string, seperated with dashes
    For example '01-03-2012' returns 'Mar'
    """
    short_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return short_months[int(month_str.split("-")[1]) - 1]


def parse_iso_date(d):
    """Parse a string representation of a date into a datetime object"""
    try:
        return datetime.date(int(d[:4]), int(d[5:7]), int(d[8:10]))
    except (ValueError, TypeError):
        return None


def previous_months_generator(d):
    """Returns a generator object with the previous month for a given datetime object"""
    year = d.year
    month = d.month
    for i in range(0, 12):
        month -= 1
        if month <= 0:
            year -= 1
            month = 12
        yield year, month


# Store lists of previous months
previous_months = [
    "{}-{}".format(year, str(month).zfill(2)) for year, month in previous_months_generator(datetime.date.today())
]
previous_months_reversed = list(reversed(previous_months))

# Store the current month as a string
today = datetime.date.today()
this_month = "{}-{}".format(today.year, str(today.month).zfill(2))

# Store a list of the past 12 months from today
previous_month_days = [today - relativedelta(months=x) for x in range(13)]
previous_year_days = [today - relativedelta(years=x) for x in range(6)]

# Store the current month and year numbers
this_month_number = datetime.datetime.today().month
this_year = datetime.datetime.today().year

# Load all the data from 'gitaggregate-publisher-dated' into memory
gitaggregate_publisher = JSONDir(filepaths.join_stats_path("gitaggregate-publisher-dated"))


def publisher_frequency_generate_row(publisher):
    """Generate the publisher frequency data"""

    agg = gitaggregate_publisher[publisher]

    # Skip to the next publisher if there is no data for 'most_recent_transaction_date' for this publisher
    if "most_recent_transaction_date" not in agg:
        return {}

    # Skip if this publisher appears in the list of publishers who have since changed their Registry ID
    if publisher in get_registry_id_matches().keys():
        return {}

    updates_per_month = defaultdict(int)
    previous_transaction_date = datetime.date(1, 1, 1)

    # Find the most recent transaction date and parse into a datetime object
    for gitdate, transaction_date_str in sorted(agg["most_recent_transaction_date"].items()):
        transaction_date = parse_iso_date(transaction_date_str)

        # If transaction date has increased
        if transaction_date is not None and transaction_date > previous_transaction_date:
            previous_transaction_date = transaction_date
            updates_per_month[gitdate[:7]] += 1

    # Find the first date that this publisher made data available, and parse into a datetime object
    first_published_string = sorted(agg["most_recent_transaction_date"])[0]
    first_published = parse_iso_date(first_published_string)

    # Implement the assessment logic on https://analytics.codeforiati.org/timeliness.html#h_assesment

    if first_published >= previous_month_days[3]:
        # This is a publisher of less than 3 months
        first_published_band = "Less than 3 months ago"
        frequency = "Annual"
    elif first_published >= previous_month_days[6]:
        # This is a publisher of less than 6 months
        first_published_band = "3-6 months ago"
        if all([x in updates_per_month for x in previous_months[:3]]):
            frequency = "Monthly"
        else:
            frequency = "Annual"
    elif first_published >= previous_month_days[12]:
        # This is a publisher of less than 12 months
        first_published_band = "6-12 months ago"
        if [x in updates_per_month for x in previous_months[:6]].count(True) >= 4:
            frequency = "Monthly"
        elif any([x in updates_per_month for x in previous_months[:3]]) and any(
            [x in updates_per_month for x in previous_months[3:6]]
        ):
            frequency = "Quarterly"
        else:
            frequency = "Annual"
    else:
        if first_published >= previous_year_days[3]:
            first_published_band = "1-3 years ago"
        elif first_published >= previous_year_days[5]:
            first_published_band = "3-5 years ago"
        else:
            first_published_band = "More than 5 years ago"
        # This is a publisher of 1 year or more
        if ([x in updates_per_month for x in previous_months[:12]].count(True) >= 7) and (
            [x in updates_per_month for x in previous_months[:2]].count(True) >= 1
        ):
            # Data updated in 7 or more of past 12 full months AND data updated at least once in last 2 full months.
            frequency = "Monthly"
        elif ([x in updates_per_month for x in previous_months[:12]].count(True) >= 3) and (
            [x in updates_per_month for x in previous_months[:4]].count(True) >= 1
        ):
            # Data updated in 3 or more of past 12 full months AND data updated at least once in last 4 full months.
            frequency = "Quarterly"
        elif any([x in updates_per_month for x in previous_months[:6]]) and any(
            [x in updates_per_month for x in previous_months[6:12]]
        ):
            # There has been an update in 2 of the last 6 month periods
            frequency = "Six-Monthly"
        elif any([x in updates_per_month for x in previous_months[:12]]):
            # There has been an update in 1 of the last 12 months
            frequency = "Annual"
        else:
            # There has been an update in none of the last 12 months
            frequency = "Less than Annual"

    return {
        "updates_per_month": updates_per_month,
        "frequency": frequency,
        "first_published_band": first_published_band,
    }


def frequency_index(frequency):
    return ["Monthly", "Quarterly", "Six-Monthly", "Annual", "Less than Annual"].index(frequency)


def timelag_index(timelag):
    return ["One month", "A quarter", "Six months", "One year", "More than one year"].index(timelag)


def first_published_band_index(first_published_band):
    return [
        "More than 5 years ago",
        "3-5 years ago",
        "1-3 years ago",
        "6-12 months ago",
        "3-6 months ago",
        "Less than 3 months ago",
    ].index(first_published_band)


def has_future_transactions(publisher):
    """
    returns 0, 1 or 2
    Returns 2 if the most recent data for a publisher has future transactions.
    Returns 1 if the publisher has ever had future transactions.
    Returns 0 otherwise.
    """
    today = datetime.date.today()
    publisher_stats = get_publisher_stats(publisher)
    if "transaction_dates" in publisher_stats:
        for transaction_type, transaction_counts in publisher_stats["transaction_dates"].items():
            for transaction_date_string, count in transaction_counts.items():
                transaction_date = parse_iso_date(transaction_date_string)
                if transaction_date and transaction_date > datetime.date.today():
                    return 2

    gitaggregate_publisher = JSONDir(filepaths.join_stats_path("gitaggregate-publisher-dated")).get(publisher, {})
    mindate = datetime.date(today.year - 1, today.month, 1)
    for date_string, latest_transaction_date_string in gitaggregate_publisher.get(
        "latest_transaction_date", {}
    ).items():
        date = parse_iso_date(date_string)
        latest_transaction_date = parse_iso_date(latest_transaction_date_string)
        if date >= mindate and latest_transaction_date and latest_transaction_date > date:
            return 1
    return 0
