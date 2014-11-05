from data import publishers_ordered_by_title#, get_publisher_stats

column_headers = {
    'core': [
        'Version',
        'Reporting-Org',
        'Iati-identifier',
        'Participating Organisation',
        'Title',
        'Description',
        'Status',
        'Activity Date',
        'Sector',
        'Country or Region'
    ],
    'financials':[
        'Transaction - Commitment',
        'Transaction - Disbursement or Expenditure',
        'Transaction - Traceability',
        'Budget'
    ],
    'valueadded':[
        'Contacts',
        'Location Details',
        'Geographic Coordinates',
        'DAC Sectors',
        'Economic Classification',
        'Activity Documents',
        'Activity Website',
        'Recipient Language',
        'Conditions Attached',
        'Result/Indicator'
    ]}


def table(tab):
    for publisher_title, publisher in publishers_ordered_by_title:
        #publisher_stats = get_publisher_stats(publisher)
        row = {}
        row['publisher'] = publisher
        row['publisher_title'] = publisher_title
        yield row

