# This file converts a range coverage data to variables which can be outputted on the coverage page
import csv
from data import get_publisher_stats
from data import get_registry_id_matches
from data import publisher_name
from data import publishers_ordered_by_title
from data import secondary_publishers

def is_number(s):
    """ Tests if a variable is a number.
        Input: s - a variable
        Return: True if v is a number
                False if v is not a number
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

def convert_to_int(x):
    """ Converts a variable to an integer value, or 0 if it cannot be converted to an integer.
        Input: x - a variable
        Return: x as an integer, or zero if x is not a number
    """
    if is_number(x):
        return int(x)
    else:
        return 0


def generate_row(publisher):
    """Generate coverage table data for a given publisher
    """

    # Store the data for this publisher as new variables
    publisher_stats = get_publisher_stats(publisher)
    transactions_usd = publisher_stats['sum_transactions_by_type_by_year_usd']

    # Create a list for publisher data, and populate it with basic data
    row = {}
    row['publisher'] = publisher
    row['publisher_title'] = publisher_name[publisher]
    row['no_data_flag_red'] = 0
    row['no_data_flag_amber'] = 0
    row['spend_data_error_reported_flag'] = 0
    row['sort_order'] = 0


    # Compute 2014 IATI spend
    iati_2014_spend_total = 0


    if publisher in dfi_publishers:
        # If this publisher is a DFI, then their 2014 spend total should be based on their
        # commitment transactions only. See https://github.com/IATI/IATI-Dashboard/issues/387
        if '2014' in transactions_usd.get('2', {}).get('USD', {}):
            iati_2014_spend_total += transactions_usd['2']['USD']['2014']

        if '2014' in transactions_usd.get('C', {}).get('USD', {}):
            iati_2014_spend_total += transactions_usd['C']['USD']['2014']

    else:
        # This is a non-DFI publisher
        if '2014' in transactions_usd.get('3', {}).get('USD', {}):
            iati_2014_spend_total += transactions_usd['3']['USD']['2014']

        if '2014' in transactions_usd.get('D', {}).get('USD', {}):
            iati_2014_spend_total += transactions_usd['D']['USD']['2014']

        if '2014' in transactions_usd.get('4', {}).get('USD', {}):
            iati_2014_spend_total += transactions_usd['4']['USD']['2014']

        if '2014' in transactions_usd.get('E', {}).get('USD', {}):
            iati_2014_spend_total += transactions_usd['E']['USD']['2014']

    # Convert to millions USD
    row['iati_spend_2014'] = round(float( iati_2014_spend_total / 1000000), 2)


    # Compute 2015 IATI spend
    iati_2015_spend_total = 0

    if publisher in dfi_publishers:
        # If this publisher is a DFI, then their 2015 spend total should be based on their
        # commitment transactions only. See https://github.com/IATI/IATI-Dashboard/issues/387
        if '2015' in transactions_usd.get('2', {}).get('USD', {}):
            iati_2015_spend_total += transactions_usd['2']['USD']['2015']

        if '2015' in transactions_usd.get('C', {}).get('USD', {}):
            iati_2015_spend_total += transactions_usd['C']['USD']['2015']

    else:
        # This is a non-DFI publisher
        if '2015' in transactions_usd.get('3', {}).get('USD', {}):
            iati_2015_spend_total += transactions_usd['3']['USD']['2015']

        if '2015' in transactions_usd.get('D', {}).get('USD', {}):
            iati_2015_spend_total += transactions_usd['D']['USD']['2015']

        if '2015' in transactions_usd.get('4', {}).get('USD', {}):
            iati_2015_spend_total += transactions_usd['4']['USD']['2015']

        if '2015' in transactions_usd.get('E', {}).get('USD', {}):
            iati_2015_spend_total += transactions_usd['E']['USD']['2015']

    # Convert to millions USD
    row['iati_spend_2015'] = round(float( iati_2015_spend_total / 1000000), 2)

    # Compute 2016 IATI spend
    iati_2016_spend_total = 0

    if publisher in dfi_publishers:
        # If this publisher is a DFI, then their 2016 spend total should be based on their
        # commitment transactions only. See https://github.com/IATI/IATI-Dashboard/issues/387
        if '2016' in transactions_usd.get('2', {}).get('USD', {}):
            iati_2016_spend_total += transactions_usd['2']['USD']['2016']

        if '2016' in transactions_usd.get('C', {}).get('USD', {}):
            iati_2016_spend_total += transactions_usd['C']['USD']['2016']

    else:
        # This is a non-DFI publisher
        if '2016' in transactions_usd.get('3', {}).get('USD', {}):
            iati_2016_spend_total += transactions_usd['3']['USD']['2016']

        if '2016' in transactions_usd.get('D', {}).get('USD', {}):
            iati_2016_spend_total += transactions_usd['D']['USD']['2016']

        if '2016' in transactions_usd.get('4', {}).get('USD', {}):
            iati_2016_spend_total += transactions_usd['4']['USD']['2016']

        if '2016' in transactions_usd.get('E', {}).get('USD', {}):
            iati_2016_spend_total += transactions_usd['E']['USD']['2016']

    # Convert to millions USD
    row['iati_spend_2016'] = round(float( iati_2015_spend_total / 1000000), 2)


    # Get reference data
    # Get data from stats files. Set as empty stings if the IATI-Stats code did not find them in the reference data sheet
    data_2014 = publisher_stats['reference_spend_data_usd'].get('2014', {'ref_spend': '', 'not_in_sheet': True})
    data_2015 = publisher_stats['reference_spend_data_usd'].get('2015', {'ref_spend': '', 'official_forecast': '', 'not_in_sheet': True})

    # Compute reference data as $USDm
    row['reference_spend_2014'] = round((float(data_2014['ref_spend']) / 1000000), 2) if is_number(data_2014['ref_spend']) else '-'
    row['reference_spend_2015'] = round((float(data_2015['ref_spend']) / 1000000), 2) if is_number(data_2015['ref_spend']) else '-'
    row['official_forecast_2015'] = round((float(data_2015['official_forecast']) / 1000000), 2) if is_number(data_2015['official_forecast']) else '-'


    # Compute spend ratio score
    # Compile a list of ratios for spend & reference data paired by year
    spend_ratio_candidates = [(row['iati_spend_2014'] / row['reference_spend_2014']) if (row['reference_spend_2014'] > 0) and is_number(row['reference_spend_2014']) else 0,
                              (row['iati_spend_2015'] / row['reference_spend_2015']) if (row['reference_spend_2015'] > 0) and is_number(row['reference_spend_2015']) else 0,
                              (row['iati_spend_2015'] / row['official_forecast_2015']) if (row['official_forecast_2015'] > 0) and is_number(row['official_forecast_2015']) else 0]

    # If there are no annual pairs, add the value of non-matching-year spend / reference data
    if ((row['iati_spend_2014'] == 0 or row['reference_spend_2014'] == '-') and
        (row['iati_spend_2015'] == 0 or row['reference_spend_2015'] == '-') and
        (row['iati_spend_2015'] == 0 or row['official_forecast_2015'] == '-')):
        spend_ratio_candidates.append((row['iati_spend_2015'] / row['reference_spend_2014']) if (row['reference_spend_2014'] > 0) and is_number(row['reference_spend_2014']) else 0)
        spend_ratio_candidates.append((row['iati_spend_2016'] / row['reference_spend_2015']) if (row['reference_spend_2015'] > 0) and is_number(row['reference_spend_2015']) else 0)
        spend_ratio_candidates.append((row['iati_spend_2016'] / row['reference_spend_2014']) if (row['reference_spend_2014'] > 0) and is_number(row['reference_spend_2014']) else 0)


    # Get the maximum value and convert to a percentage
    row['spend_ratio'] = int(round(max(spend_ratio_candidates) * 100))


    # Compute coverage score and raise to the top of its quintile
    # or set to default 20% where there is no data, or a data error is reported
    if publisher_stats['reference_spend_data_usd'].get('spend_data_error_reported', False):
        # For publishers where a data error is reported, set their score to 20%
        row['coverage_adjustment'] = 20
        row['spend_data_error_reported_flag'] = 1
        row['sort_order'] = 3

    elif all([row['reference_spend_2014'] == '-', row['reference_spend_2015'] == '-', row['official_forecast_2015'] == '-']):
        # For publishers where no reference data has been found, set their score to 20%
        row['coverage_adjustment'] = 20

        if data_2014.get('not_in_sheet', False) and data_2015.get('not_in_sheet', False):
            # This is a new publisher, who was not known when reference data was collected
            row['no_data_flag_amber'] = 1
            row['sort_order'] = 2
        else:
            # This is a known publisher, who appears in the reference data sheet (albeit with no data)
            row['no_data_flag_red'] = 1
            row['sort_order'] = 1

    elif row['spend_ratio'] > 120 and not publisher_stats['reference_spend_data_usd'].get('DAC', False):
        # Suggestion that if apend ratio is over 100%, then generally something is wrong with the data
        # Margin of 20% leeway given otherwise bumping coverage adjustment down to 20% due to data quality issues.
        # Note that this does not apply to DAC publishers
        # Full detail: https://github.com/IATI/IATI-Dashboard/issues/400
        row['coverage_adjustment'] = 20

    elif row['spend_ratio'] >= 80:
        row['coverage_adjustment'] = 100

    elif row['spend_ratio'] >= 60:
        row['coverage_adjustment'] = 80

    elif row['spend_ratio'] >= 40:
        row['coverage_adjustment'] = 60

    else:
        row['coverage_adjustment'] = 40

    return row


def table():
    """Generate coverage table data for every publisher and return as a generator object
    """

    # Loop over each publisher
    for publisher_title, publisher in publishers_ordered_by_title:

        # Store the data for this publisher as new variables
        publisher_stats = get_publisher_stats(publisher)

        # Skip if all activities from this publisher are secondary reported
        if publisher in secondary_publishers:
            continue

        # Return a generator object
        yield generate_row(publisher)


# Compile a list of Development finance institutions (DFIs)
with open('dfi_publishers.csv', 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    dfi_publishers = []
    for line in reader:

        # Update the publisher registry ID, if this publisher has since updated their registry ID
        if line[1] in get_registry_id_matches().keys():
            line[1] = get_registry_id_matches()[line[1]]

        # Append publisher ID to the list of dfi publishers, if they are found in the list of publisher IDs
        if line[1] in [x[1] for x in publishers_ordered_by_title]:
            dfi_publishers.append(line[1])
