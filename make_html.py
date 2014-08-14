import sys, os, re, copy
import subprocess
import urllib
from collections import defaultdict

from flask import Flask, render_template, redirect, Response
app = Flask(__name__)

print 'Doing initial data import'
from data import *
print 'Initial data import finished'

top_titles = {
    'index': 'Home',
    'headlines': 'Headlines',
    'data_quality': 'Data Quality',
    'exploring_data': 'Exploring Data',
    'github': 'GitHub',
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
    'annualreport' : 'Annual Report Stats',
    'coverage' : 'Coverage',
    'timeliness' : 'Timeliness',
    'forwardlooking' : 'Forward Looking'
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
    'annualreport': 'NOTE: This page is very much a work in progress, and currently the methodology differs subtly from the Annual Report.',
    'coverage': 'NOTE: This page is a work in progress. Currently publishers using non-USD or multiple currencies will have no perenctage calculated.',
    'timeliness': 'NOTE: This page is a work in progress.',
    'forwardlooking': 'NOTE: This page is a work in progress. Spend is the sum of all disbrusements and expenditure. * indicates that a result is missing because mutiple/different currencies have been used, but currency conversion is not yet implemented.'
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
    'annualreport' : 'Overview',
})

top_navigation = ['index', 'headlines', 'data_quality', 'exploring_data', 'github', 'faq']
navigation = {
    'headlines': [ 'publishers', 'files', 'activities'],
    'data_quality': ['download', 'xml', 'validation', 'versions', 'licenses', 'organisation', 'identifiers', 'reporting_orgs'],
    'exploring_data': ['elements', 'codelists', 'booleans', 'dates'],
    'github': ['github', 'milestones', 'milestones-completed'],
    'annualreport': ['annualreport', 'coverage', 'timeliness', 'forwardlooking']
}

def dictinvert(d):
    inv = defaultdict(list)
    for k, v in d.iteritems():
        inv[v].append(k)
    return inv

def dataset_to_publisher(publisher_slug):
    """ Converts a dataset (package) slug e.g. dfid-bd to the corresponding publisher
    slug e.g. dfid """
    return publisher_slug.rsplit('-',1)[0]

def iati_stats_page(template, **kwargs):
    def f():
        return render_template(template,
            current_stats=current_stats,
            ckan=ckan,
            ckan_publishers=ckan_publishers,
            publisher_name={publisher:publisher_json['result']['title'] for publisher,publisher_json in ckan_publishers.items()},
            data_tickets=data_tickets,
            get_publisher_stats=get_publisher_stats,
            set=set,
            **kwargs) 
    return f

def firstint(s):
    if s[0].startswith('<'): return 0
    m = re.search('\d+', s[0])
    return int(m.group(0))

def xpath_to_url(path):
    path = path.strip('./')
    if path.startswith('iati-activity'):
        return 'http://iatistandard.org/activity-standard/iati-activities/'+path.split('@')[0]
    elif path.startswith('iati-organisation'):
        return 'http://iatistandard.org/activity-standard/iati-organisations/'+path.split('@')[0]
    else:
        return 'http://iatistandard.org/activity-standard/iati-activities/iati-activity/'+path.split('@')[0]

def registration_agency(orgid):
    for code in codelist_sets['OrganisationRegistrationAgency']:
        if orgid.startswith(code):
            return code

app.jinja_env.filters['xpath_to_url'] = xpath_to_url
app.jinja_env.filters['url_to_filename'] = lambda x: x.split('/')[-1]
app.jinja_env.filters['dataset_to_publisher'] = dataset_to_publisher
app.jinja_env.globals['url'] = lambda x: x
app.jinja_env.globals['datetime_generated'] = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %z']).strip()
app.jinja_env.globals['datetime_data'] = max(gitdate.values())
app.jinja_env.globals['stats_url'] = 'http://dashboard.iatistandard.org/stats'
#app.jinja_env.globals['stats_url'] = 'http://localhost:8001'
app.jinja_env.globals['sorted'] = sorted
app.jinja_env.globals['enumerate'] = enumerate
app.jinja_env.globals['top_titles'] = top_titles 
app.jinja_env.globals['page_titles'] = page_titles 
app.jinja_env.globals['short_page_titles'] = short_page_titles 
app.jinja_env.globals['page_leads'] = page_leads
app.jinja_env.globals['page_sub_leads'] = page_sub_leads
app.jinja_env.globals['top_navigation'] = top_navigation
app.jinja_env.globals['navigation'] = navigation
app.jinja_env.globals['navigation_reverse'] = { page:k for k,pages in navigation.items() for page in pages }
app.jinja_env.globals['navigation_reverse'].update({ k:k for k in navigation})

def make_slugs(keys):
    out = {'by_slug':{}, 'by_i':{}}
    for i,key in enumerate(keys):
        slug = re.sub('[^a-zA-Z0-9:@\-_]', '', re.sub('{[^}]*}', '', key.replace('{http://www.w3.org/XML/1998/namespace}','xml:').replace('/','_'))).strip('_')
        while slug in out:
            slug += '_'
        out['by_slug'][slug] = i
        out['by_i'][i] = slug
    return out
slugs = {
    'codelist': make_slugs(current_stats['inverted_publisher']['codelist_values'].keys()),
    'element': make_slugs(current_stats['inverted_publisher']['elements'].keys())
}
app.jinja_env.globals['slugs'] = slugs

from vars import expected_versions
import github.web, licenses
urls = {
    'index.html': iati_stats_page('index.html', page='index'),
    'headlines.html': iati_stats_page('headlines.html', page='headlines'),
    'data_quality.html': iati_stats_page('data_quality.html', page='data_quality'),
    'exploring_data.html': iati_stats_page('exploring_data.html', page='exploring_data'),
    'publishers.html': iati_stats_page('publishers.html', page='publishers'),
    'annualreport.html': iati_stats_page('annualreport.html', page='annualreport', annualreport_columns = {
        '1.1': 'Timeliness of transaction data',
        '1.2': 'Frequency of updates',
        '1.3': 'Activity Forward Planning',
        '1.4': 'Transaction Alignment with Recipient Financial Year',
        '1.5': 'Budget Alignment with Recipient Financial Year',
        '2.1': 'Unique identifier',
        '2.2': 'Use of Recipient language',
        '2.3': 'Start Date',
        '2.4': 'End Date',
        '2.5': 'Implementing Organisation',
        '2.6': 'Accountable Organisation',
        '3.1': 'Sub-national Geography (text)',
        '3.2': 'Sub-national Geography (geocoding)',
        '3.3': 'CRS Sector',
        '5.1': 'Commitments',
        '5.2': 'Disbursements and Expenditure',
        '5.3': 'Traceable Income and Disbursements',
        '6.1': 'Activity Documents',
        '6.2': 'Text of Conditions',
        '6.3': 'Results data (text)',
        '6.4': 'Results data (structured)'
        
    }),
    'coverage.html': iati_stats_page('coverage.html', page='coverage', dac2012=dac2012, float=float),
    'timeliness.html': iati_stats_page('timeliness.html', page='timeliness'),
    'forwardlooking.html': iati_stats_page('forwardlooking.html', page='forwardlooking'),
    'files.html': iati_stats_page('files.html', page='files', firstint=firstint),
    'activities.html': iati_stats_page('activities.html', page='activities'),
    'download.html': iati_stats_page('download.html', page='download'),
    'xml.html': iati_stats_page('xml.html', page='xml'),
    'validation.html': iati_stats_page('validation.html', page='validation'),
    'versions.html': iati_stats_page('versions.html', page='versions', expected_versions=expected_versions),
    'licenses.html': licenses.main,
    'organisation.html': iati_stats_page('organisation.html', page='organisation'),
    'identifiers.html': iati_stats_page('identifiers.html', page='identifiers'),
    'reporting_orgs.html': iati_stats_page('reporting_orgs.html', page='reporting_orgs'),
    'elements.html': iati_stats_page('elements.html', page='elements'),
    'codelists.html': iati_stats_page('codelists.html', page='codelists', codelist_mapping=codelist_mapping, codelist_sets=codelist_sets),
    'booleans.html': iati_stats_page('booleans.html', page='booleans'),
    'dates.html': iati_stats_page('dates.html', page='dates'),
    'data/download_errors.json': lambda: Response(json.dumps(current_stats['download_errors'], indent=2), mimetype='application/json'),
    'github.html': github.web.main,
    'milestones.html': github.web.milestones,
    'milestones-completed.html': github.web.milestones_closed,
    'faq.html': iati_stats_page('faq.html', page='faq'),
}

app.route('/')(lambda: redirect('index.html'))

@app.route('/publisher/<publisher>.html')
def publisher(publisher):
    publisher_stats = get_publisher_stats(publisher)
    budget_table = [ {
            'year': 'Total',
            'count_total': sum(sum(x.values()) for x in publisher_stats['count_budgets_by_type_by_year'].values()),
            'sum_total': { currency:sum(sums.values()) for by_currency in publisher_stats['sum_budgets_by_type_by_year'].values() for currency,sums in by_currency.items()  },
            'count_original': sum(publisher_stats['count_budgets_by_type_by_year']['1'].values()) if '1' in publisher_stats['count_budgets_by_type_by_year'] else None,
            'sum_original': { k:sum(v.values()) for k,v in publisher_stats['sum_budgets_by_type_by_year']['1'].items() } if '1' in publisher_stats['count_budgets_by_type_by_year'] else None,
            'count_revised': sum(publisher_stats['count_budgets_by_type_by_year']['2'].values()) if '2' in publisher_stats['count_budgets_by_type_by_year'] else None,
            'sum_revised': { k:sum(v.values()) for k,v in publisher_stats['sum_budgets_by_type_by_year']['2'].items() } if '2' in publisher_stats['count_budgets_by_type_by_year'] else None
        } ] + [
            {
                'year': year,
                'count_total': sum(x[year] for x in publisher_stats['count_budgets_by_type_by_year'].values() if year in x),
                'sum_total': { currency:sums.get(year) for by_currency in publisher_stats['sum_budgets_by_type_by_year'].values() for currency,sums in by_currency.items()  },
                'count_original': publisher_stats['count_budgets_by_type_by_year']['1'].get(year) if '1' in publisher_stats['count_budgets_by_type_by_year'] else None,
                'sum_original': { k:v.get(year) for k,v in publisher_stats['sum_budgets_by_type_by_year']['1'].items() } if '1' in publisher_stats['count_budgets_by_type_by_year'] else None,
                'count_revised': publisher_stats['count_budgets_by_type_by_year']['2'].get(year) if '2' in publisher_stats['count_budgets_by_type_by_year'] else None,
                'sum_revised': { k:v.get(year) for k,v in publisher_stats['sum_budgets_by_type_by_year']['2'].items() } if '2' in publisher_stats['count_budgets_by_type_by_year'] else None
            } for year in sorted(set(sum((x.keys() for x in publisher_stats['count_budgets_by_type_by_year'].values()), [])))
        ]
    return iati_stats_page('publisher.html',
        url=lambda x: '../'+x,
        publisher=publisher,
        publisher_stats=publisher_stats,
        publisher_inverted=get_publisher_stats(publisher, 'inverted-file'),
        publisher_licenses=licenses.licenses_for_publisher(publisher),
        codelist_mapping=codelist_mapping,
        codelist_sets=codelist_sets,
        budget_table=budget_table
        )()

@app.route('/codelist/<slug>.html')
def codelist(slug):
    i = slugs['codelist']['by_slug'][slug]
    element = current_stats['inverted_publisher']['codelist_values'].keys()[i]
    values = current_stats['inverted_publisher']['codelist_values'].values()[i]
    return iati_stats_page('codelist.html',
        element=element,
        values=values,
        codelist_mapping=codelist_mapping,
        reverse_codelist_mapping=dictinvert(codelist_mapping),
        codelist_sets=codelist_sets,
        url=lambda x: '../'+x,
        page='codelists')()

@app.route('/element/<slug>.html')
def element(slug):
    i = slugs['element']['by_slug'][slug]
    element = current_stats['inverted_publisher']['elements'].keys()[i]
    publishers = current_stats['inverted_publisher']['elements'].values()[i]
    file_grouped = current_stats['inverted_file_grouped']['elements'].values()[i]
    return iati_stats_page('element.html',
        element=element,
        publishers=publishers,
        file_grouped=file_grouped,
        url=lambda x: '../'+x,
        page='elements')()

app.route('/license/<license>.html')(licenses.individual_license)

@app.route('/registration_agencies.html')
def registration_agencies():
    registration_agencies = defaultdict(int)
    registration_agencies_publishers = defaultdict(list)
    nonmatching = []
    for orgid, publishers in current_stats['inverted_publisher']['reporting_orgs'].items():
        reg_ag = registration_agency(orgid)
        if reg_ag:
            registration_agencies[reg_ag] += 1
            registration_agencies_publishers[reg_ag] += publishers.keys()
        else:
            nonmatching.append((orgid, publishers))
    return iati_stats_page('registration_agencies.html',
        page='registration_agencies',
        registration_agencies=registration_agencies,
        registration_agencies_publishers=registration_agencies_publishers,
        nonmatching=nonmatching)()

def make_html(urls, outdir=''):
    for url, f in urls.items():
        full_url = outdir+'/'+url
        if callable(f):
            f.__name__ = full_url.replace('.','_').encode('utf-8')
            app.add_url_rule(full_url, view_func=f)
        else:
            make_html(f, full_url)

# Server an image through the development server (--live)
@app.route('/<image>.png')
def image_development(image):
    print image
    return Response(open(os.path.join('out', image+'.png')).read(), mimetype='image/png')

@app.route('/publisher_imgs/<image>.png')
def image_development_publisher(image):
    print image
    return Response(open(os.path.join('out', 'publisher_imgs', image+'.png')).read(), mimetype='image/png')

make_html(urls)

if __name__ == '__main__':
    if '--live' in sys.argv:
        app.debug = True
        app.run()
    else:
        from flask_frozen import Freezer
        app.config['FREEZER_DESTINATION'] = 'out'
        app.config['FREEZER_REMOVE_EXTRA_FILES'] = False
        freezer = Freezer(app)

        @freezer.register_generator
        def url_generator():
            for publisher in current_stats['inverted_publisher']['activities'].keys():
                yield 'publisher', {'publisher':publisher}
            for slug in slugs['element']['by_slug']: 
                yield 'element', {'slug':slug}
            for slug in slugs['codelist']['by_slug']: 
                yield 'codelist', {'slug':slug}
            for license in licenses.licenses: 
                if license == None:
                    license = 'None'
                yield 'individual_license', {'license':license}
            

        freezer.freeze()
