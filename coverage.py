# This file converts a range coverage data to variables which can be outputted on the coverage page
import csv
from data import get_publisher_stats
from data import get_registry_id_matches
from data import publishers_ordered_by_title

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


def table():
    """Generate data for the publisher coverage table
    """

    # Loop over each publisher
    for publisher_title, publisher in publishers_ordered_by_title:

        # Store the data for this publisher as new variables
        publisher_stats = get_publisher_stats(publisher)
        transactions_usd = publisher_stats['sum_transactions_by_type_by_year_usd']
        
        # Skip if all activities from this publisher are secondary reported
        if int(publisher_stats['activities']) == len(publisher_stats['activities_secondary_reported']):
            continue

        # Create a list for publisher data, and populate it with basic data
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title
        row['no_data_flag'] = 0
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


        # Get reference data 
        # Get data from stats files. Set as zero if the keys do not exist
        data_2014 = publisher_stats['reference_spend_data_usd'].get('2014', {'ref_spend': 0})
        data_2015 = publisher_stats['reference_spend_data_usd'].get('2015', {'ref_spend': 0, 'official_forecast': 0})

        # Compute reference data as $USDm
        row['reference_spend_2014'] = round((float(data_2014['ref_spend']) / 1000000), 2) if is_number(data_2014['ref_spend']) else '-'
        row['reference_spend_2015'] = round((float(data_2015['ref_spend']) / 1000000), 2) if is_number(data_2015['ref_spend']) else '-'
        row['official_forecast_2015'] = round((float(data_2015['official_forecast']) / 1000000), 2) if is_number(data_2015['official_forecast']) else '-'


        # Compute spend ratio score
        spend_ratio = max([(row['iati_spend_2014'] / row['reference_spend_2014']) if (row['reference_spend_2014'] > 0) and is_number(row['reference_spend_2014']) else 0, 
                           (row['iati_spend_2015'] / row['reference_spend_2015']) if (row['reference_spend_2015'] > 0) and is_number(row['reference_spend_2015']) else 0,
                           (row['iati_spend_2015'] / row['reference_spend_2014']) if (row['reference_spend_2014'] > 0) and is_number(row['reference_spend_2014']) else 0,
                           (row['iati_spend_2015'] / row['official_forecast_2015']) if (row['official_forecast_2015'] > 0) and is_number(row['official_forecast_2015']) else 0])
        row['spend_ratio'] = int(spend_ratio * 100)


        # Compute coverage score and raise to the top of its quintile
        # or set to default 20% where there is no data, or a data error is reported
        if publisher_stats['reference_spend_data_usd'].get('spend_data_error_reported', False):
            # For publishers where a data error is reported, set their score to 20%
            row['coverage_adjustment'] = 20
            row['spend_data_error_reported_flag'] = 1
            row['sort_order'] = 2

        elif all([row['reference_spend_2014'] == '-', row['reference_spend_2015'] == '-', row['official_forecast_2015'] == '-']):
            # For publishers with no data found, set their score to 20%
            row['coverage_adjustment'] = 20
            row['no_data_flag'] = 1
            row['sort_order'] = 1

        elif row['spend_ratio'] >= 80:
            row['coverage_adjustment'] = 100

        elif row['spend_ratio'] >= 60:
            row['coverage_adjustment'] = 80

        elif row['spend_ratio'] >= 40:
            row['coverage_adjustment'] = 60

        else:
            row['coverage_adjustment'] = 40


        # Return a generator object
        yield row


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
