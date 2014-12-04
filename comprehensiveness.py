from data import publishers_ordered_by_title, get_publisher_stats

columns = {
    'core': [
        ('version', 'Version'),
        ('reporting-org', 'Reporting-Org'),
        ('iati-identifier', 'Iati-identifier'),
        ('participating-org', 'Participating Organisation'),
        ('title', 'Title'),
        ('description', 'Description'),
        ('activity-status', 'Status'),
        ('activity-date', 'Activity Date'),
        ('sector', 'Sector'),
        ('country_or_region', 'Country or Region'),
    ],
    'financials': [
        ('transaction_commitment', 'Transaction - Commitment'),
        ('transaction_spend', 'Transaction - Disbursement or Expenditure'),
        ('transaction_traceability', 'Transaction - Traceability'),
        ('budget', 'Budget'),
    ],
    'valueadded':[
        ('contact-info', 'Contacts'),
        ('location', 'Location Details'),
        ('location_point_pos', 'Geographic Coordinates'),
        ('sector_dac', 'DAC Sectors'),
        ('capital-spend', 'Capital Spend'),
        ('document-link', 'Activity Documents'),
        ('activity-website', 'Activity Website'),
        ('title_recipient_language', 'Recipient Language'),
        ('conditions_attached', 'Conditions Attached'),
        ('result_indicator', 'Result/Indicator)'),
    ]}
column_headers = {tabname:[x[1] for x in values] for tabname, values in columns.items()}
column_slugs = {tabname:[x[0] for x in values] for tabname, values in columns.items()}


def table():
    for publisher_title, publisher in publishers_ordered_by_title:
        publisher_stats = get_publisher_stats(publisher)
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title
        def denominator(key):
            if key in publisher_stats['comprehensiveness_denominators']:
                return int(publisher_stats['comprehensiveness_denominators'][key])
            else:
                return int(publisher_stats['comprehensiveness_denominator_default'])
        for k,v in publisher_stats['comprehensiveness'].items():
            if denominator(k) != 0:
                row[k] = int(float(v)/denominator(k)*100)

        for k,v in publisher_stats['comprehensiveness_with_validation'].items():
            if denominator(k) != 0:
                row[k+'_valid'] = int(float(v)/denominator(k)*100)
        yield row

