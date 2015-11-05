# This file converts a range coverage data to variables which can be outputted on the coverage page

from data import publishers_ordered_by_title, get_publisher_stats


def is_number(s):
    """ @todo Document this function
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

def convert_to_int(x):
    """ @todo Document this function
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

        # Store the data for this publisher as a new variable
        publisher_stats = get_publisher_stats(publisher)
        
        # Create a list for publisher data, and populate it with basic data
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title


        # Compute IATI spend
        iati_spend_total = 0
        transactions_usd = publisher_stats['sum_transactions_by_type_by_year_usd']

        if '2014' in transactions_usd.get('3', {}).get('USD', {}):
            iati_spend_total += transactions_usd['3']['USD']['2014']

        if '2014' in transactions_usd.get('D', {}).get('USD', {}):
            iati_spend_total += transactions_usd['D']['USD']['2014']

        if '2014' in transactions_usd.get('4', {}).get('USD', {}):
            iati_spend_total += transactions_usd['4']['USD']['2014']

        if '2014' in transactions_usd.get('E', {}).get('USD', {}):
            iati_spend_total += transactions_usd['E']['USD']['2014']

        # Convert to millions USD 
        row['iati_spend'] = float( iati_spend_total / 1000000)


        # Compute coverage score
        row['coverage_score'] = 100



        # Return a generator object
        yield row

