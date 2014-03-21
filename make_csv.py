import unicodecsv
import os
import data
from collections import OrderedDict

publisher_name = {p['name']:p['title'] for p in data.ckan_publishers['result']}

def publisher_dicts():
    for publisher, activities in data.current_stats['inverted_publisher']['activities'].items():
        publisher_stats = data.get_publisher_stats(publisher) 
        yield {
            'Publisher Name': publisher_name[publisher],
            'Publisher Registry Id': publisher,
            'Activities': activities,
            'Organisations': publisher_stats['organisations'],
            'Files': publisher_stats['activity_files']+publisher_stats['organisation_files'],
            'Activity Files': publisher_stats['activity_files'],
            'Organisation Files': publisher_stats['organisation_files'],
            'Total File Size': publisher_stats['file_size'],
            'Reporting Orgs (count)': len(publisher_stats['reporting_orgs']),
            'Reporting Orgs': ';'.join(publisher_stats['reporting_orgs']),
            'Data Tickets': len(data.data_tickets[publisher])
        }

with open(os.path.join('out', 'publishers.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, [
        'Publisher Name',
        'Publisher Registry Id',
        'Activities',
        'Organisations',
        'Files',
        'Activity Files',
        'Organisation Files',
        'Total File Size',
        'Reporting Orgs (count)',
        'Reporting Orgs',
        'Data Tickets',
        ])
    writer.writeheader()
    for d in publisher_dicts():
        writer.writerow(d)
