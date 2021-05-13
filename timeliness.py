# This file converts raw timeliness data into the associated Publishing Statistics assessments

from data import JSONDir, publisher_name, get_publisher_stats, get_registry_id_matches
import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict, Counter


def short_month(month_str):
    """Return the 'short month' represeentation of a date which is inputted as a string, seperated with dashes
       For example '01-03-2012' returns 'Mar'
    """
    short_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return short_months[int(month_str.split('-')[1]) - 1]


def parse_iso_date(d):
    """Parse a string representation of a date into a datetime object
    """
    try:
        return datetime.date(int(d[:4]), int(d[5:7]), int(d[8:10]))
    except (ValueError, TypeError):
        return None


def previous_months_generator(d):
    """Returns a generator object with the previous month for a given datetime object
    """
    year = d.year
    month = d.month
    for i in range(0, 12):
        month -= 1
        if month <= 0:
            year -= 1
            month = 12
        yield year, month


# Store lists of previous months
previous_months = ['{}-{}'.format(year, str(month).zfill(2)) for year, month in previous_months_generator(datetime.date.today())]
previous_months_reversed = list(reversed(previous_months))

# Store the current month as a string
today = datetime.date.today()
this_month = '{}-{}'.format(today.year, str(today.month).zfill(2))

# Store a list of the past 12 months from today
previous_month_days = [today - relativedelta(months=x) for x in range(1, 13)]

# Store the current month and year numbers
this_month_number = datetime.datetime.today().month
this_year = datetime.datetime.today().year


def publisher_frequency():
    """Generate the publisher frequency data
    """

    # Load all the data from 'gitaggregate-publisher-dated' into memory
    gitaggregate_publisher = JSONDir('./stats-calculated/gitaggregate-publisher-dated')

    # Loop over each publisher - i.e. a publisher folder within 'gitaggregate-publisher-dated'
    for publisher, agg in gitaggregate_publisher.items():

        # Skip to the next publisher if there is no data for 'most_recent_transaction_date' for this publisher
        if 'most_recent_transaction_date' not in agg:
            continue

        # Skip if this publisher appears in the list of publishers who have since changed their Registry ID
        if publisher in get_registry_id_matches().keys():
            continue

        updates_per_month = defaultdict(int)
        previous_transaction_date = datetime.date(1, 1, 1)

        # Find the most recent transaction date and parse into a datetime object
        for gitdate, transaction_date_str in sorted(agg['most_recent_transaction_date'].items()):
            transaction_date = parse_iso_date(transaction_date_str)

            # If transaction date has increased
            if transaction_date is not None and transaction_date > previous_transaction_date:
                previous_transaction_date = transaction_date
                updates_per_month[gitdate[:7]] += 1

        # Find the first date that this publisher made data available, and parse into a datetime object
        first_published_string = sorted(agg['most_recent_transaction_date'])[0]
        first_published = parse_iso_date(first_published_string)

        hft = has_future_transactions(publisher)

        # Implement the assessment logic on https://analytics.codeforiati.org/timeliness.html#h_assesment

        if first_published >= previous_month_days[2]:
            # This is a publisher of less than 3 months
            first_published_band = 'Less than 3 months ago'
            frequency = 'Annual'
        elif first_published >= previous_month_days[5]:
            # This is a publisher of less than 6 months
            first_published_band = 'Less than 6 months ago'
            if all([x in updates_per_month for x in previous_months[:3]]):
                frequency = 'Monthly'
            else:
                frequency = 'Annual'
        elif first_published >= previous_month_days[11]:
            # This is a publisher of less than 12 months
            first_published_band = 'Less than 1 year ago'
            if [x in updates_per_month for x in previous_months[:6]].count(True) >= 4:
                frequency = 'Monthly'
            elif any([x in updates_per_month for x in previous_months[:3]]) and any([x in updates_per_month for x in previous_months[3:6]]):
                frequency = 'Quarterly'
            else:
                frequency = 'Annual'
        else:
            first_published_band = 'More than 1 year ago'
            # This is a publisher of 1 year or more
            if ([x in updates_per_month for x in previous_months[:12]].count(True) >= 7) and ([x in updates_per_month for x in previous_months[:2]].count(True) >= 1):
                # Data updated in 7 or more of past 12 full months AND data updated at least once in last 2 full months.
                frequency = 'Monthly'
            elif ([x in updates_per_month for x in previous_months[:12]].count(True) >= 3) and ([x in updates_per_month for x in previous_months[:4]].count(True) >= 1):
                # Data updated in 3 or more of past 12 full months AND data updated at least once in last 4 full months.
                frequency = 'Quarterly'
            elif any([x in updates_per_month for x in previous_months[:6]]) and any([x in updates_per_month for x in previous_months[6:12]]):
                # There has been an update in 2 of the last 6 month periods
                frequency = 'Six-Monthly'
            elif any([x in updates_per_month for x in previous_months[:12]]):
                # There has been an update in 1 of the last 12 months
                frequency = 'Annual'
            else:
                # There has been an update in none of the last 12 months
                frequency = 'Less than Annual'

        # If the publisher is in the list of current publishers, return a generator object
        if publisher in publisher_name:
            yield publisher, publisher_name.get(publisher), updates_per_month, frequency, hft, first_published_band


def frequency_index(frequency):
    return ['Monthly', 'Quarterly', 'Six-Monthly', 'Annual', 'Less than Annual'].index(frequency)


def publisher_frequency_sorted():
    return sorted(
        publisher_frequency(),
        key=lambda tup: (frequency_index(tup[3]), tup[1]))


def publisher_frequency_dict():
    publisher_data_list = sorted(publisher_frequency(), key=lambda publisher: publisher[0])
    data = {}
    for v in publisher_data_list:
        data[v[0]] = v
    return data


def publisher_frequency_summary():
    return Counter(frequency for _, _, _, frequency, _, _ in publisher_frequency())


def timelag_index(timelag):
    return ['One month', 'A quarter', 'Six months', 'One year', 'More than one year'].index(timelag)


def first_published_band_index(first_published_band):
    return ['More than 1 year ago', 'Less than 1 year ago', 'Less than 6 months ago', 'Less than 3 months ago'].index(first_published_band)


def publisher_timelag_sorted():
    publisher_timelags = [(publisher, publisher_name.get(publisher), agg['transaction_months_with_year'], agg['timelag'], has_future_transactions(publisher)) for publisher, agg in JSONDir('./stats-calculated/current/aggregated-publisher').items()]
    return sorted(
        publisher_timelags,
        key=lambda tup: (timelag_index(tup[3]), tup[1]))


def publisher_timelag_dict():
    publisher_timelags = [(publisher, publisher_name.get(publisher), agg['transaction_months_with_year'], agg['timelag'], has_future_transactions(publisher)) for publisher, agg in JSONDir('./stats-calculated/current/aggregated-publisher').items()]
    data = {}
    for v in publisher_timelags:
        data[v[0]] = v
    return data


def publisher_timelag_summary():
    return Counter(timelag for _, _, _, timelag, _ in publisher_timelag_sorted())


def has_future_transactions(publisher):
    """
        returns 0, 1 or 2
        Returns 2 if the most recent data for a publisher has future transactions.
        Returns 1 if the publisher has ever had future transactions.
        Returns 0 otherwise.
    """
    today = datetime.date.today()
    publisher_stats = get_publisher_stats(publisher)
    if 'transaction_dates' in publisher_stats:
        for transaction_type, transaction_counts in publisher_stats['transaction_dates'].items():
            for transaction_date_string, count in transaction_counts.items():
                transaction_date = parse_iso_date(transaction_date_string)
                if transaction_date and transaction_date > datetime.date.today():
                    return 2

    gitaggregate_publisher = JSONDir('./stats-calculated/gitaggregate-publisher-dated').get(publisher, {})
    mindate = datetime.date(today.year - 1, today.month, 1)
    for date, activity_blacklist in gitaggregate_publisher.get('activities_with_future_transactions', {}).items():
        if parse_iso_date(date) >= mindate and activity_blacklist:
            return 1
    return 0


def sort_first(list_, key):
    return sorted(list_, key=lambda x: key(x[0]))
