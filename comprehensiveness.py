from data import publishers_ordered_by_title, get_publisher_stats

columns = {
    'summary': [
        # (slug, header, weighting)
        ('core_average', 'Core Average', 1),
        ('financials_average', 'Financials Average', 1),
        ('valueadded_average', 'Value Added Average', 1),
        ('summary_average', 'Average', 0), # don't include the average in the average
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
        ('core_average', 'Average', 0), # don't include the average in the average
    ],
    'financials': [
        ('transaction_commitment', 'Transaction - Commitment', 1),
        ('transaction_spend', 'Transaction - Disbursement or Expenditure', 1),
        ('transaction_traceability', 'Transaction - Traceability', 1),
        ('budget', 'Budget', 1),
        ('financials_average', 'Average', 0), # don't include the average in the average
    ],
    'valueadded':[
        ('contact-info', 'Contacts', 1),
        ('location', 'Location Details', 1),
        ('location_point_pos', 'Geographic Coordinates', 1),
        ('sector_dac', 'DAC Sectors', 1),
        ('capital-spend', 'Capital Spend', 1),
        ('document-link', 'Activity Documents', 1),
        ('activity-website', 'Activity Website', 1),
        ('title_recipient_language', 'Recipient Language (TBC)', 0),
        ('conditions_attached', 'Conditions Attached', 1),
        ('result_indicator', 'Result/ Indicator', 1),
        ('valueadded_average', 'Average', 0), # don't include the average in the average
    ]}
column_headers = {tabname:[x[1] for x in values] for tabname, values in columns.items()}
column_slugs = {tabname:[x[0] for x in values] for tabname, values in columns.items()}


def denominator(key, stats):
    if not stats:
        return 0
    if key in stats['comprehensiveness_denominators']:
        return int(stats['comprehensiveness_denominators'][key])
    else:
        return int(stats['comprehensiveness_denominator_default'])


def table():
    for publisher_title, publisher in publishers_ordered_by_title:
        publisher_stats = get_publisher_stats(publisher)
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title

        for k,v in publisher_stats['comprehensiveness'].items():
            if k not in column_slugs['financials']:
                if denominator(k, publisher_stats) != 0:
                    row[k] = int(float(v)/denominator(k, publisher_stats)*100)
        # https://github.com/IATI/IATI-Dashboard/issues/278
        if 'comprehensiveness' in publisher_stats['bottom_hierarchy']:
            for k,v in publisher_stats['bottom_hierarchy']['comprehensiveness'].items():
                if k in column_slugs['financials']:
                    if denominator(k, publisher_stats['bottom_hierarchy']) != 0:
                        row[k] = int(float(v)/denominator(k, publisher_stats['bottom_hierarchy'])*100)

        for k,v in publisher_stats['comprehensiveness_with_validation'].items():
            if k not in column_slugs['financials']:
                if denominator(k, publisher_stats) != 0:
                    row[k+'_valid'] = int(float(v)/denominator(k, publisher_stats)*100)
        # https://github.com/IATI/IATI-Dashboard/issues/278
        if 'comprehensiveness_with_validation' in publisher_stats['bottom_hierarchy']:
            for k,v in publisher_stats['bottom_hierarchy']['comprehensiveness_with_validation'].items():
                if k in column_slugs['financials']:
                    if denominator(k, publisher_stats['bottom_hierarchy']) != 0:
                        row[k+'_valid'] = int(float(v)/denominator(k, publisher_stats['bottom_hierarchy'])*100)

        for page in ['core', 'financials', 'valueadded', 'summary']: 
            # summary must be last to use calculations from others
            row[page+'_average'] = sum((row.get(x[0]) or 0)*x[2] for x in columns[page]) / sum(x[2] for x in columns[page])
            row[page+'_average_valid'] = sum((row.get(x[0]+'_valid') or 0)*x[2] for x in columns[page]) / sum(x[2] for x in columns[page])

        yield row

