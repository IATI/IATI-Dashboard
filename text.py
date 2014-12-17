import copy

top_titles = {
    'index': 'Home',
    'headlines': 'Headlines',
    'data_quality': 'Data Quality',
    'exploring_data': 'Exploring Data',
    'github': 'GitHub',
    'publishing_stats': 'Publishing Statistics',
    'faq': 'FAQ'
}

page_titles = {
    'index': 'IATI Dashboard',
    'headlines': 'Headlines',
    'data_quality': 'Data Quality',
    'exploring_data': 'Exploring Data',
    'faq': 'IATI Dashboard Frequently Asked Questions',
    'publishers': 'IATI Publishers',
    'files': 'IATI Files',
    'activities': 'IATI Activities',
    'download' : 'Download Errors',
    'xml' : 'XML Errors',
    'validation' : 'Validation Against the Schema',
    'versions' : 'Versions',
    'rulesets' : 'Rulesets',
    'licenses' : 'Licenses listed on the Registry',
    'organisation' : 'Organisation XML Files',
    'identifiers' : 'Duplicate Activity Identifiers',
    'registration_agencies' : 'Registration Agencies',
    'reporting_orgs' : 'Reporting Orgs',
    'elements' : 'Elements',
    'codelists' : 'Codelists',
    'booleans' : 'Booleans',
    'dates' : 'Dates',
    'github': 'GitHub Overview',
    'milestones' : 'GitHub Milestones',
    'milestones-completed' : 'GitHub Milestones (Completed)',
    'publishing_stats': 'Publishing Statistics',
    'coverage' : 'Coverage',
    'timeliness' : 'Timeliness',
    'forwardlooking' : 'Forward Looking',
    'comprehensiveness': 'Comprehensiveness'
}

page_leads = {
    'index': 'The IATI Dashboard provides statistics, charts and metrics on data accessed via the IATI Registry.',
    'data_quality': 'What needs fixing in IATI data?',
    'exploring_data': 'Which parts of the IATI Standard are being used?',
    'headlines': 'What is the size, scope and scale of published IATI data?',
    'publishers': 'How many organisations are publishing IATI data?',
    'files': 'How many IATI files are published?',
    'activities': 'How many IATI activities are published?',
    'download': 'How many files failed to download?',
    'xml': 'Which files have XML errors?',
    'validation': 'Which files fail schema validation?',
    'versions': 'Which <a href="http://iatistandard.org/upgrades/all-versions/">versions of the IATI Standard</a> are being used?',
    'rulesets': 'How does IATI data test against rulesets?',
    'licenses': 'Which licences are used by IATI publishers?',
    'organisation': 'Who is publishing IATI Organisation files?',
    'identifiers': 'Where are there duplicate IATI identifiers?',
    'reporting_orgs': 'Where are reporting organisation identifiers inconsistent with the IATI Registry?',
    'elements': 'How are the IATI Standard elements used by publishers?',
    'codelists': 'How are codelists used in IATI data?',
    'booleans': 'How are booleans used in IATI data?',
    'github': 'What are the IATI team doing in GitHub?',
    'milestones': 'What is planned by the IATI team in GitHub?',
    'milestones-completed': 'What has been done by the IATI team in GitHub?',
    'dates': 'What date ranges do publishers publish data for?',
}
page_sub_leads = {
    'publishers': 'Publishers represent organisation accounts in the IATI Registry.',
    'files': 'Files are logged on the IATI Registry by publishers The files contain data on activities and the organisation.  A publisher may have multiple files, which can contain multiple activities.',
    'activities': 'Activities are the individual projects found in files.  A file can contain one or many activities, from a publisher.',
    'download': 'Files that failed to download, when accessed via the IATI Registry. Note: These files failed to download in the nightly routine. This may because no URL is listed on the registry, or when requesting the URL the publisher\'s server returns an error message (e.g. because there is no file at that location). Since the dashboard\'s download occurs nightly, some files that failed to download then may now be available.',
    'xml': 'This page shows files that are not well-formed XML, accessed via the IATI Registry. ',
    'validation': 'IATI files are validated against the appropriate <a href="http://iatistandard.org/schema/">IATI Schema</a>. Note: this is based on the version declared in the file and whether it\'s an activity/organisation file.',
    'versions': 'Files are reported against a specific version of the IATI Standard, using the <code>version</code> attribute in the <code>iati-activities</code> element.',
    'rulesets': 'The IATI Ruleset describe constraints, conditions and logics that are additional to the IATI schema. Note: Currently, on the IATI Standard Ruleset is tested.',
    'licenses': 'Licences are applied to files by publishers on the IATI Registry, and explain how data can be used. ',
    'organisation': 'Checking the IATI Registry for files that have <code>iati-organisations</code> as the root element. IATI Organisation files contain general information about the organisations in the delivery chain. ',
    'identifiers': 'Checking the <code>iati-identifier</code> element for duplicate values per publisher. A duplicate appears if a publisher creates two activities with the same identifier.',
    'reporting_orgs': 'Checking the <code>reporting-org</code> identifiers in IATI data.',
    'elements': 'Checking usage of all elements within the IATI Standard.',
    'codelists': 'Checking usage of codelists across IATI data files.',
    'booleans': 'Checking usage of booleans across IATI data files. Booleans are values that are either true or false. In XML <code>true</code> or <code>1</code> can be used for true and <code>false</code> or <code>0</code> can be used for false.',
    'github': 'Overview numbers from the <a href="https://github.com/IATI">IATI GitHub organisation</a>. GitHub is an online repository used by open-source developers to help them manage their work. The IATI team use it for a variety of reasons, including logging issues in software and guidance.',
    'milestones': 'Calendar of the due dates of all open milestones in every repository belonging to the <a href="https://github.com/IATI">IATI organisation on GitHub</a>.',
    'milestones-completed': 'Calendar of all CLOSED milestones in every repository belonging to the <a href="https://github.com/IATI">IATI organisation on GitHub</a>.',
}

short_page_titles = copy.copy(page_titles)
short_page_titles.update({
    'publishers': 'Publishers',
    'files': 'Files',
    'activities': 'Activities',
    'validation': 'Validation',
    'licenses' : 'Licenses',
    'organisation' : 'Organisation XML',
    'identifiers' : 'Duplicate Identifiers',
    'github': 'Overview',
    'milestones' : 'Milestones',
    'milestones-completed' : 'Completed Milestones',
})

top_navigation = ['index', 'headlines', 'data_quality', 'exploring_data', 'github', 'publishing_stats', 'faq']
navigation = {
    'headlines': [ 'publishers', 'files', 'activities'],
    'data_quality': ['download', 'xml', 'validation', 'versions', 'licenses', 'organisation', 'identifiers', 'reporting_orgs'],
    'exploring_data': ['elements', 'codelists', 'booleans', 'dates'],
    'github': ['github', 'milestones', 'milestones-completed'],
    'publishing_stats': ['timeliness', 'forwardlooking']#, 'comprehensiveness'] #, 'coverage' ]
}
