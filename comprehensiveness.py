# This file converts raw comprehensiveness data to percentages, and calculates averages.

from data import publishers_ordered_by_title, get_publisher_stats, publisher_name

columns = {
    'summary': [
        # Format for elements within this list - and similar lists below ('core', 'financials', etc):
        # slug, header, weighting when calculating average
        ('core_average', 'Core Average', 2),
        ('financials_average', 'Financials Average', 1),
        ('valueadded_average', 'Value Added Average', 1),
        ('summary_average', 'Weighted Average', 0),  # i.e. don't include the average within the calculation of the average
    ],
    'core': [
        ('version', 'Version', 1),
        ('reporting-org', 'Reporting-Org', 1),
        ('iati-identifier', 'Iati-identifier', 1),
        ('participating-org', 'Participating Organisation', 1),
        ('title', 'Title', 1),
        ('description', 'Description', 1),
        ('activity-status', 'Status', 1),
        ('activity-date', 'Activity Date', 1),
        ('sector', 'Sector', 1),
        ('country_or_region', 'Country or Region', 1),
        ('core_average', 'Average', 0),  # i.e. don't include the average within the calculation of the average
    ],
    'financials': [
        ('transaction_commitment', 'Transaction - Commitment', 1, 'first_hierarchy_with_commitments'),
        ('transaction_spend', 'Transaction - Disbursement or Expenditure', 1, 'bottom_hierarchy'),
        ('transaction_traceability', 'Transaction - Traceability', 1, 'bottom_hierarchy'),
        ('budget', 'Budget', 1, 'hierarchy_with_most_budgets'),
        ('financials_average', 'Average', 0),  # i.e. don't include the average within the calculation of the average
    ],
    'valueadded': [
        ('contact-info', 'Contacts', 1),
        ('location', 'Location Details', 1),
        ('location_point_pos', 'Geographic Coordinates', 1),
        ('sector_dac', 'DAC Sectors', 1),
        ('capital-spend', 'Capital Spend', 1),
        ('document-link', 'Activity Documents', 1),
        ('aid_type', 'Aid Type', 1),
        ('recipient_language', 'Recipient Language', 1),
        ('result_indicator', 'Result/ Indicator', 1),
        ('valueadded_average', 'Average', 0),  # i.e. don't include the average within the calculation of the average
    ]}

# Build dictionaries for all the column_headers and column_slugs defined above
column_headers = {tabname: [x[1] for x in values] for tabname, values in columns.items()}
column_slugs = {tabname: [x[0] for x in values] for tabname, values in columns.items()}

# Build directory to lookup the hierarchy which should be used in the numerator
# e.g. {'activity-date': 'all', 'activity-status': 'all', [...] budget': 'hierarchy_with_most_budgets', [etc]}
column_base_lookup = {
    col[0]: col[3] if len(col) > 3 else 'all'
    for col_group, col_components in columns.items()
    for col in col_components
}


def denominator(key, stats):
    """Return the appropriate denominator value for a given key.
    Returns either the specifc demominator calculated, or a default denominator value.
    """

    # If stats not pased to this function, return zero
    if not stats:
        return 0

    # If there is a specific denominator for the given key, return this
    if key in stats['comprehensiveness_denominators']:
        return int(stats['comprehensiveness_denominators'][key])

    # Otherwise, return the default denominator
    else:
        return int(stats['comprehensiveness_denominator_default'])


def get_hierarchy_with_most_budgets(stats):
    """Find the hierarchy which contains the greatest number of budgets.
       Will only count hierarchies where the default denominator is greater than zero.
       Input:
         stats -- a JSONDir object of publisher stats
       Returns:
         Key of the hierarchy with greatest number of budgets, or None
    """

    try:
        # Get the key with the largest number of budgets
        budgets = max(stats['by_hierarchy'], key=(
            lambda x:
            stats['by_hierarchy'][x]['comprehensiveness'].get('budget', 0) + stats['by_hierarchy'][x]['comprehensiveness'].get('budget_not_provided', 0)
            if stats['by_hierarchy'][x]['comprehensiveness_denominator_default'] > 0 else -1)
        )
        return budgets
    except KeyError:
        # Return None if this publisher has no comprehensiveness data in any hierarchy - i.e. KeyError
        return None
    except ValueError:
        # Some publishers have no data in 'by_hierarchy' at all - i.e. ValueError: max() arg is an empty sequence
        return None


def get_first_hierarchy_with_commitments(stats):
    """Return the number of the first hierarchy that contains at least 1 commitment
       (according to the comprehensiveness counts)
       Returns:
         Number of first hierarchy with commitments or None if no commitments in any hierarchy
    """
    hierarchies_with_commitments = {x: y['comprehensiveness']['transaction_commitment']
                                    for x, y in stats.get('by_hierarchy', {}).items()
                                    if y['comprehensiveness'].get('transaction_commitment', 0) > 0}
    return min(hierarchies_with_commitments) if len(hierarchies_with_commitments) else None


def generate_row(publisher):
    """Generate comprehensiveness table data for a given publisher
    """

    publisher_stats = get_publisher_stats(publisher)

    # Set an inital dictionary, which will later be populated further
    row = {}
    row['publisher'] = publisher
    row['publisher_title'] = publisher_name[publisher]

    # Calculate percentages for publisher data populated with any data
    for slug in column_slugs['core'] + column_slugs['financials'] + column_slugs['valueadded']:

        # Set the stats base for calculating the numerator. This is based on the hierarchy set in the lookup
        if column_base_lookup[slug] == 'bottom_hierarchy':
            publisher_base = publisher_stats.get('bottom_hierarchy', {})

        elif column_base_lookup[slug] == 'hierarchy_with_most_budgets':
            publisher_base = publisher_stats['by_hierarchy'].get(get_hierarchy_with_most_budgets(publisher_stats), {})

        elif column_base_lookup[slug] == 'first_hierarchy_with_commitments':
            if get_first_hierarchy_with_commitments(publisher_stats):
                publisher_base = publisher_stats['by_hierarchy'].get(get_first_hierarchy_with_commitments(publisher_stats), {})
            else:
                publisher_base = publisher_stats.get('bottom_hierarchy', {})

        else:
            # Most common case will be column_base_lookup[slug] == 'all':
            publisher_base = publisher_stats

        if slug == 'budget':
            budget_all = publisher_base.get('comprehensiveness', {}).get(slug, 0)
            budget_not_provided_all = publisher_base.get('comprehensiveness', {}).get('budget_not_provided', 0)
            numerator_all = budget_all + budget_not_provided_all
            budget_valid = publisher_base.get('comprehensiveness_with_validation', {}).get(slug, 0)
            budget_not_provided_valid = publisher_base.get('comprehensiveness_with_validation', {}).get('budget_not_provided', 0)
            numerator_valid = budget_valid + budget_not_provided_valid
        else:
            numerator_all = publisher_base.get('comprehensiveness', {}).get(slug, 0)
            numerator_valid = publisher_base.get('comprehensiveness_with_validation', {}).get(slug, 0)

        if denominator(slug, publisher_base) != 0:
            # Populate the row with the %age
            row[slug] = int(round(
                float(numerator_all) / denominator(slug, publisher_base) * 100
            ))
            row[slug + '_valid'] = int(round(
                float(numerator_valid) / denominator(slug, publisher_base) * 100
            ))

    # Loop for averages
    # Calculate the average for each grouping, and the overall 'summary' average
    for page in ['core', 'financials', 'valueadded', 'summary']:
        # Note that the summary must be last, so that it can use the average calculations from the other groupings
        row[page + '_average'] = int(round(
            sum((row.get(x[0]) or 0) * x[2] for x in columns[page]) / float(sum(x[2] for x in columns[page]))
        ))
        row[page + '_average_valid'] = int(round(
            sum((row.get(x[0] + '_valid') or 0) * x[2] for x in columns[page]) / float(sum(x[2] for x in columns[page]))
        ))

    return row


def table():
    """Generate comprehensiveness table data for every publisher and return as a generator object
    """

    # Loop over the data for each publisher
    for publisher_title, publisher in publishers_ordered_by_title:

        # Generate a row object
        yield generate_row(publisher)
