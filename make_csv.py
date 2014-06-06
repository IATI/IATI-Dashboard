import unicodecsv
import os
import data
from collections import OrderedDict

publisher_name={publisher:publisher_json['result']['title'] for publisher,publisher_json in data.ckan_publishers.items()}

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
            'Reporting Org on Registry': data.ckan_publishers[publisher]['result']['publisher_iati_id'],
            'Reporting Orgs in Data (count)': len(publisher_stats['reporting_orgs']),
            'Reporting Orgs in Data': ';'.join(publisher_stats['reporting_orgs']),
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
        'Reporting Org on Registry',
        'Reporting Orgs in Data (count)',
        'Reporting Orgs in Data',
        'Data Tickets',
        ])
    writer.writeheader()
    for d in publisher_dicts():
        writer.writerow(d)



publishers = data.current_stats['inverted_publisher']['activities'].keys()

with open(os.path.join('out', 'elements.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, [ 'Element' ] + publishers )
    writer.writeheader()
    for element, publisher_dict in data.current_stats['inverted_publisher']['elements'].items():
        publisher_dict['Element'] = element
        writer.writerow(publisher_dict)

with open(os.path.join('out', 'elements_total.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, [ 'Element' ] + publishers )
    writer.writeheader()
    for element, publisher_dict in data.current_stats['inverted_publisher']['elements_total'].items():
        publisher_dict['Element'] = element
        writer.writerow(publisher_dict)

