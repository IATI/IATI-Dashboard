from __future__ import print_function
from data import JSONDir, publisher_name, get_publisher_stats
import datetime
from collections import defaultdict

def parse_iso_date(d):
    try:
        return datetime.date(int(d[:4]), int(d[5:7]), int(d[8:10]))
    except ValueError:
        return None

def previous_months_generator(d):
    year = d.year
    month = d.month
    for i in range(0,12):
        month -= 1
        if month <= 0:
            year -= 1
            month = 12
        yield year,month

previous_months = ['{}-{}'.format(year,str(month).zfill(2)) for year,month in previous_months_generator(datetime.date.today())]
previous_months_reversed=list(reversed(previous_months))
this_month = '{}-{}'.format(year,str(month).zfill(2))

previous_month_starts = [datetime.date(year,month,1) for year,month in previous_months_generator(datetime.date.today()) ]

def publisher_frequency():
    gitaggregate_publisher = JSONDir('./stats-calculated/gitaggregate-publisher-dated')
    for publisher, agg in gitaggregate_publisher.items():
        if not 'most_recent_transaction_date' in agg:
            continue
        updates_per_month = defaultdict(int)
        previous_transaction_date = ''
        for gitdate, transaction_date in sorted(agg['most_recent_transaction_date'].items()):
            if transaction_date != previous_transaction_date:
                previous_transaction_date = transaction_date
                updates_per_month[gitdate[:7]] += 1
        first_published_string = sorted(agg['most_recent_transaction_date'])[0]
        first_published = parse_iso_date(first_published_string)
        if first_published >= previous_month_starts[2]:
            #if True in [ x in updates_per_month for x in previous_months[:3] ]:
            frequency = 'Annual'
        elif first_published >= previous_month_starts[5]:
            if all([ x in updates_per_month for x in previous_months[:3] ]):
                frequency = 'Monthly'
            else:
                frequency = 'Annual'
        elif first_published >= previous_month_starts[11]:
            if [ x in updates_per_month for x in previous_months[:6] ].count(True) >= 4:
                frequency = 'Monthly'
            elif any([ x in updates_per_month for x in previous_months[:3] ]) and any([ x in updates_per_month for x in previous_months[3:6] ]):
                frequency = 'Quarterly'
            else:
                frequency = 'Annual'
        else:
            if [ x in updates_per_month for x in previous_months[:12] ].count(True) >= 9:
                frequency = 'Monthly'
            elif [ any([ x in updates_per_month for x in previous_months[start:end] ]) for start,end in [(0,3),(3,6),(6,9),(9,12)] ].count(True) >= 3:
                frequency = 'Quarterly'
            elif any([ x in updates_per_month for x in previous_months[:6] ]) and any([ x in updates_per_month for x in previous_months[6:12] ]):
                frequency = 'Six-Monthly'
            else:
                frequency = 'Less than Annual'
        yield publisher, publisher_name.get(publisher), updates_per_month, frequency

def publisher_frequency_sorted():
    return sorted(publisher_frequency(), key=lambda (publisher, publisher_title , _, frequency): (
        ['Monthly', 'Quarterly', 'Six-Monthly', 'Annual', 'Less than Annual'].index(frequency),
        publisher_title
        ))

def publisher_timelag_sorted():
    publisher_timelags = [ (publisher, publisher_name.get(publisher), agg['transaction_months_with_year'], agg['timelag']) for publisher,agg in JSONDir('./stats-calculated/current/aggregated-publisher').items() ]
    return sorted(publisher_timelags, key=lambda (publisher, publisher_title, _, timelag): (
        ['One month', 'A quarter', 'Six months', 'One year', 'More than one year'].index(timelag),
        publisher_title
        ))

def has_future_transactions(publisher):
    print(publisher)
    publisher_stats = get_publisher_stats(publisher)
    for transaction_type, transaction_counts in publisher_stats['transaction_dates'].items():
        for transaction_date_string, count in transaction_counts.items():
            transaction_date = parse_iso_date(transaction_date_string)
            if transaction_date and transaction_date > datetime.date.today():
                return True
    return False

