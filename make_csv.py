# Script to generate CSV files from data in the 'stats-calculated' folder,
# and extra logic in other files in this repository

import unicodecsv
import os
import data
from collections import OrderedDict
import timeliness
import comprehensiveness
import summary_stats
import forwardlooking
import humanitarian

publisher_name = {publisher: publisher_json['result']['title'] for publisher, publisher_json in data.ckan_publishers.items()}


def publisher_dicts():
    for publisher, activities in data.current_stats['inverted_publisher']['activities'].items():
        if publisher in publisher_name:
            publisher_stats = data.get_publisher_stats(publisher)
            yield {
                'Publisher Name': publisher_name[publisher],
                'Publisher Registry Id': publisher,
                'Activities': activities,
                'Hierarchies (count)': len(publisher_stats['hierarchies']),
                'Hierarchies': ';'.join(publisher_stats['hierarchies']),
            }


with open(os.path.join('out', 'publishers.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, [
        'Publisher Name',
        'Publisher Registry Id',
        'Activities',
        'Hierarchies (count)',
        'Hierarchies',
    ])
    writer.writeheader()
    for d in publisher_dicts():
        writer.writerow(d)

publishers = data.current_stats['inverted_publisher']['activities'].keys()

with open(os.path.join('out', 'elements.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, ['Element'] + publishers)
    writer.writeheader()
    for element, publisher_dict in data.current_stats['inverted_publisher']['elements'].items():
        publisher_dict['Element'] = element
        writer.writerow(publisher_dict)

with open(os.path.join('out', 'elements_total.csv'), 'w') as fp:
    writer = unicodecsv.DictWriter(fp, ['Element'] + publishers)
    writer.writeheader()
    for element, publisher_dict in data.current_stats['inverted_publisher']['elements_total'].items():
        publisher_dict['Element'] = element
        writer.writerow(publisher_dict)

with open(os.path.join('out', 'registry.csv'), 'w') as fp:
    keys = ['name', 'title', 'publisher_frequency', 'publisher_frequency_select', 'publisher_implementation_schedule', 'publisher_ui', 'publisher_field_exclusions', 'publisher_contact', 'image_url', 'display_name', 'publisher_iati_id', 'publisher_units', 'publisher_record_exclusions', 'publisher_data_quality', 'publisher_country', 'publisher_description',  'publisher_refs', 'publisher_thresholds' 'publisher_agencies', 'publisher_constraints', 'publisher_organization_type', 'publisher_segmentation', 'license_id', 'state', 'publisher_timeliness']
    writer = unicodecsv.DictWriter(fp, keys)
    writer.writeheader()
    for publisher_json in data.ckan_publishers.values():
        writer.writerow({x: publisher_json['result'].get(x) or 0 for x in keys})

# Timeliness CSV files (frequency and timelag)
previous_months = timeliness.previous_months_reversed

for fname, f, assessment_label in (
    ('timeliness_frequency.csv', timeliness.publisher_frequency_sorted, 'Frequency'),
    ('timeliness_timelag.csv', timeliness.publisher_timelag_sorted, 'Time lag')
):
    with open(os.path.join('out', fname), 'w') as fp:
        writer = unicodecsv.writer(fp)
        writer.writerow(['Publisher Name', 'Publisher Registry Id'] + previous_months + [assessment_label])
        for publisher, publisher_title, per_month, assessment in f():
            writer.writerow([publisher_title, publisher] + [per_month.get(x) or 0 for x in previous_months] + [assessment])

# Forward-looking CSV file
with open(os.path.join('out', 'forwardlooking.csv'), 'w') as fp:
    writer = unicodecsv.writer(fp)
    writer.writerow(['Publisher Name', 'Publisher Registry Id'] + ['{} ({})'.format(header, year) for header in forwardlooking.column_headers for year in forwardlooking.years])
    for row in forwardlooking.table():
        writer.writerow([row['publisher_title'], row['publisher']] + [year_column[year] for year_column in row['year_columns'] for year in forwardlooking.years])

# Comprehensiveness CSV files ('summary', 'core', 'financials' and 'valueadded')
for tab in comprehensiveness.columns.keys():
    with open(os.path.join('out', 'comprehensiveness_{}.csv'.format(tab)), 'w') as fp:
        writer = unicodecsv.writer(fp)
        if tab == 'financials':
            writer.writerow(['Publisher Name', 'Publisher Registry Id'] +
                            [x + ' (with valid data)' for x in comprehensiveness.column_headers[tab]] +
                            [x + ' (with any data)' for x in comprehensiveness.column_headers[tab]] +
                            ['Using budget-not-provided'])
            for row in comprehensiveness.table():
                writer.writerow([row['publisher_title'], row['publisher']] +
                                [row[slug + '_valid'] if slug in row else '-' for slug in comprehensiveness.column_slugs[tab]] +
                                [row[slug] if slug in row else '-' for slug in comprehensiveness.column_slugs[tab]] +
                                ['Yes' if row['flag'] else '-'])
        else:
            writer.writerow(['Publisher Name', 'Publisher Registry Id'] +
                            [x + ' (with valid data)' for x in comprehensiveness.column_headers[tab]] +
                            [x + ' (with any data)' for x in comprehensiveness.column_headers[tab]])
            for row in comprehensiveness.table():
                writer.writerow([row['publisher_title'], row['publisher']] +
                                [row[slug + '_valid'] if slug in row else '-' for slug in comprehensiveness.column_slugs[tab]] +
                                [row[slug] if slug in row else '-' for slug in comprehensiveness.column_slugs[tab]])

# Summary Stats CSV file
with open(os.path.join('out', 'summary_stats.csv'), 'w') as fp:
    writer = unicodecsv.writer(fp)
    # Add column headers
    writer.writerow(['Publisher Name', 'Publisher Registry Id'] + [header for slug, header in summary_stats.columns])
    for row in summary_stats.table():
        # Write each row
        writer.writerow([row['publisher_title'], row['publisher']] + [row[slug] for slug, header in summary_stats.columns])

# Humanitarian CSV file
with open(os.path.join('out', 'humanitarian.csv'), 'w') as fp:
    writer = unicodecsv.writer(fp)
    # Add column headers
    writer.writerow([
        'Publisher Name',
        'Publisher Registry Id',
        'Publisher Type',
        'Number of Activities',
        'Publishing Humanitarian',
        'Using Humanitarian Attribute',
        'Appeal or Emergency Details',
        'Clusters',
        'Humanitarian Score'
    ])
    for row in humanitarian.table():
        writer.writerow([
            row['publisher_title'],
            row['publisher'],
            row['publisher_type'],
            row['num_activities'],
            row['publishing_humanitarian'],
            row['humanitarian_attrib'],
            row['appeal_emergency'],
            row['clusters'],
            row['average']
        ])
