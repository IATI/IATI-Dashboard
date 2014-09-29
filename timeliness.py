from __future__ import print_function
from data import JSONDir
import datetime
from collections import defaultdict

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
        first_published = datetime.date(int(first_published_string[:4]), int(first_published_string[5:7]), int(first_published_string[8:10]))
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
        yield publisher, updates_per_month, frequency

