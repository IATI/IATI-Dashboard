# Script to generate CSV files from data in the 'stats-calculated' folder,
# and extra logic in other files in this repository
import csv
import data

# Timeliness CSV files (frequency and timelag)
import timeliness

# Forward-looking CSV file
import forwardlooking

# Comprehensiveness CSV files ('summary', 'core', 'financials' and 'valueadded')
import comprehensiveness

# # Coverage CSV file
# import coverage

# Summary Stats CSV file
import summary_stats

# Humanitarian CSV file
import humanitarian

import config

publisher_name = {publisher: publisher_json['result']['title'] for publisher, publisher_json in data.ckan_publishers.items()}


def publisher_dicts():
    for publisher, activities in data.current_stats['inverted_publisher']['activities'].items():
        if publisher not in data.ckan_publishers:
            continue
        publisher_stats = data.get_publisher_stats(publisher)
        yield {
            'Publisher Name': publisher_name[publisher],
            'Publisher Registry Id': publisher,
            'Activities': activities,
            'Organisations': publisher_stats['organisations'],
            'Files': publisher_stats['activity_files'] + publisher_stats['organisation_files'],
            'Activity Files': publisher_stats['activity_files'],
            'Organisation Files': publisher_stats['organisation_files'],
            'Total File Size': publisher_stats['file_size'],
            'Reporting Org on Registry': data.ckan_publishers[publisher]['result']['publisher_iati_id'],
            'Reporting Orgs in Data (count)': len(publisher_stats['reporting_orgs']),
            'Reporting Orgs in Data': ';'.join(publisher_stats['reporting_orgs']),
            'Hierarchies (count)': len(publisher_stats['hierarchies']),
            'Hierarchies': ';'.join(publisher_stats['hierarchies']),
        }


with open(config.join_out_path('publishers.csv'), 'w') as fp:
    writer = csv.DictWriter(fp, [
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
        'Hierarchies (count)',
        'Hierarchies',
    ])
    writer.writeheader()
    for d in publisher_dicts():
        writer.writerow(d)

publishers = list(data.current_stats['inverted_publisher']['activities'].keys())

with open(config.join_out_path('elements.csv'), 'w') as fp:
    writer = csv.DictWriter(fp, ['Element'] + publishers)
    writer.writeheader()
    for element, publisher_dict in data.current_stats['inverted_publisher']['elements'].items():
        publisher_dict['Element'] = element
        writer.writerow(publisher_dict)

with open(config.join_out_path('elements_total.csv'), 'w') as fp:
    writer = csv.DictWriter(fp, ['Element'] + publishers)
    writer.writeheader()
    for element, publisher_dict in data.current_stats['inverted_publisher']['elements_total'].items():
        publisher_dict['Element'] = element
        writer.writerow(publisher_dict)

with open(config.join_out_path('registry.csv'), 'w') as fp:
    keys = ['name', 'title', 'publisher_frequency', 'publisher_frequency_select', 'publisher_implementation_schedule', 'publisher_ui', 'publisher_field_exclusions', 'publisher_contact', 'image_url', 'display_name', 'publisher_iati_id', 'publisher_units', 'publisher_record_exclusions', 'publisher_data_quality', 'publisher_country', 'publisher_description', 'publisher_refs', 'publisher_thresholds' 'publisher_agencies', 'publisher_constraints', 'publisher_organization_type', 'publisher_segmentation', 'license_id', 'state', 'publisher_timeliness']
    writer = csv.DictWriter(fp, keys)
    writer.writeheader()
    for publisher_json in data.ckan_publishers.values():
        writer.writerow({x: publisher_json['result'].get(x) or 0 for x in keys})

previous_months = timeliness.previous_months_reversed

with open(config.join_out_path('timeliness_frequency.csv'), 'w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['Publisher Name', 'Publisher Registry Id'] + previous_months + ['Frequency', 'First published'])
    for publisher, publisher_title, per_month, assessment, hft, first_published_band in timeliness.publisher_frequency_sorted():
        writer.writerow([publisher_title, publisher] + [per_month.get(x) or 0 for x in previous_months] + [assessment, first_published_band])

with open(config.join_out_path('timeliness_timelag.csv'), 'w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['Publisher Name', 'Publisher Registry Id'] + previous_months + ['Time lag'])
    for publisher, publisher_title, per_month, assessment, hft in timeliness.publisher_timelag_sorted():
        writer.writerow([publisher_title, publisher] + [per_month.get(x) or 0 for x in previous_months] + [assessment])

with open(config.join_out_path('forwardlooking.csv'), 'w') as fp:
    writer = csv.writer(fp)
    writer.writerow(['Publisher Name', 'Publisher Registry Id'] + ['{} ({})'.format(header, year) for header in forwardlooking.column_headers for year in forwardlooking.years])
    for row in forwardlooking.table():
        writer.writerow([row['publisher_title'], row['publisher']] + [year_column[year] for year_column in row['year_columns'] for year in forwardlooking.years])

for tab in comprehensiveness.columns.keys():
    with open(config.join_out_path('comprehensiveness_{}.csv'.format(tab)), 'w') as fp:
        writer = csv.writer(fp)
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

# with open(os.path.join('out', 'coverage.csv'), 'w') as fp:
#     writer = csv.writer(fp)
#     # Add column headers
#     writer.writerow([
#         'Publisher Name',
#         'Publisher Registry Id',
#         '2014 IATI Spend (US $m)',
#         '2015 IATI Spend (US $m)',
#         '2014 Reference Spend (US $m)',
#         '2015 Reference Spend (US $m)',
#         '2015 Official Forecast (US $m)',
#         'Spend Ratio (%)',
#         'No reference data available (Historic publishers)',
#         'No reference data available (New publishers)',
#         'Data quality issue reported'
#     ])
#     for row in coverage.table():
#         # Write each row
#         writer.writerow([
#             row['publisher_title'],
#             row['publisher'],
#             row['iati_spend_2014'],
#             row['iati_spend_2015'],
#             row['reference_spend_2014'],
#             row['reference_spend_2015'],
#             row['official_forecast_2015'],
#             row['spend_ratio'],
#             row['no_data_flag_red'],
#             row['no_data_flag_amber'],
#             row['spend_data_error_reported_flag']
#         ])

with open(config.join_out_path('summary_stats.csv'), 'w') as fp:
    writer = csv.writer(fp)
    # Add column headers
    writer.writerow(['Publisher Name', 'Publisher Registry Id'] + [header for slug, header in summary_stats.columns])
    for row in summary_stats.table():
        # Write each row
        writer.writerow([row['publisher_title'], row['publisher']] + [row[slug] for slug, header in summary_stats.columns])

with open(config.join_out_path('humanitarian.csv'), 'w') as fp:
    writer = csv.writer(fp)
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
