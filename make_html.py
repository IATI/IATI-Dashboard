# Script to generate static HTML pages
# This uses Jinja templating to render the HTML templates in the 'templates' folder
# Data is based on the files in the 'stats-calculated' folder, and extra logic in other files in this repository

from __future__ import print_function
import sys
import os
import re
import subprocess
from collections import defaultdict

from flask import Flask, render_template, redirect, abort, Response
app = Flask(__name__, template_folder="static/templates")

import licenses
import timeliness
import forwardlooking
import comprehensiveness
import coverage
import transparencyindicator
from vars import expected_versions
import text
import datetime

print('Doing initial data import')
from data import *
print('Initial data import finished')


def dictinvert(d):
    inv = defaultdict(list)
    for k, v in d.iteritems():
        inv[v].append(k)
    return inv

def nested_dictinvert(d):
    inv = defaultdict(lambda: defaultdict(int))
    for k, v in d.iteritems():
        for k2, v2 in v.iteritems():
            inv[k2][k] += v2
    return inv

def dataset_to_publisher(publisher_slug):
    """ Converts a dataset (package) slug e.g. dfid-bd to the corresponding publisher
    slug e.g. dfid """
    return publisher_slug.rsplit('-',1)[0]


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
    for code in codelist_sets['2']['OrganisationRegistrationAgency']:
        if orgid.startswith(code):
            return code

def get_codelist_values(codelist_values_for_element):
    """Return a list of unique values present within a one-level nested dictionary.
       Envisaged usage is to gather the codelist values used by each publisher, as in
       stats/current/inverted-publisher/codelist_values_by_major_version.json
       Input: Set of codelist values for a given element (listed by publisher), for example:
              current_stats['inverted_publisher']['codelist_values_by_major_version']['1']['.//@xml:lang']
    """
    return list(set([y for x in codelist_values_for_element.items() for y in x[1].keys()]))

# Custom Jinja filters
app.jinja_env.filters['xpath_to_url'] = xpath_to_url
app.jinja_env.filters['url_to_filename'] = lambda x: x.split('/')[-1]
app.jinja_env.filters['dataset_to_publisher'] = dataset_to_publisher
app.jinja_env.filters['has_future_transactions'] = timeliness.has_future_transactions

# Custom Jinja globals
app.jinja_env.globals['url'] = lambda x: x
app.jinja_env.globals['datetime_generated'] = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %z']).strip()
app.jinja_env.globals['datetime_data'] = max(gitdate.values())
app.jinja_env.globals['stats_url'] = 'http://dashboard.iatistandard.org/stats'
app.jinja_env.globals['sorted'] = sorted
app.jinja_env.globals['enumerate'] = enumerate
app.jinja_env.globals['top_titles'] = text.top_titles
app.jinja_env.globals['page_titles'] = text.page_titles
app.jinja_env.globals['short_page_titles'] = text.short_page_titles
app.jinja_env.globals['page_leads'] = text.page_leads
app.jinja_env.globals['page_sub_leads'] = text.page_sub_leads
app.jinja_env.globals['top_navigation'] = text.top_navigation
app.jinja_env.globals['navigation'] = text.navigation
app.jinja_env.globals['navigation_reverse'] = { page:k for k,pages in text.navigation.items() for page in pages }
app.jinja_env.globals['navigation_reverse'].update({ k:k for k in text.navigation})
app.jinja_env.globals['current_stats'] = current_stats
app.jinja_env.globals['ckan'] = ckan
app.jinja_env.globals['ckan_publishers'] = ckan_publishers
app.jinja_env.globals['publisher_name'] = publisher_name
app.jinja_env.globals['publishers_ordered_by_title'] = publishers_ordered_by_title
app.jinja_env.globals['data_tickets'] = data_tickets
app.jinja_env.globals['get_publisher_stats'] = get_publisher_stats
app.jinja_env.globals['set'] = set
app.jinja_env.globals['firstint'] = firstint
app.jinja_env.globals['expected_versions'] = expected_versions
app.jinja_env.globals['current_year'] = datetime.datetime.now().year
# Following variables set in coverage branch but not in master
# app.jinja_env.globals['float'] = float
# app.jinja_env.globals['dac2012'] = dac2012
app.jinja_env.globals['MAJOR_VERSIONS'] = MAJOR_VERSIONS

app.jinja_env.globals['slugs'] = slugs
app.jinja_env.globals['codelist_mapping'] = codelist_mapping
app.jinja_env.globals['codelist_conditions'] = codelist_conditions
app.jinja_env.globals['codelist_sets'] = codelist_sets
app.jinja_env.globals['get_codelist_values'] = get_codelist_values

basic_page_names = [
        'index',
        'headlines',
        'data_quality',
        'exploring_data',
        'publishers',
        'publishing_stats',
        'timeliness',
        'timeliness_timelag',
        'forwardlooking',
        'comprehensiveness',
        'comprehensiveness_core',
        'comprehensiveness_financials',
        'comprehensiveness_valueadded',
        'coverage',
        'transparencyindicator',
        'files',
        'activities',
        'download',
        'xml',
        'validation',
        'versions',
        'organisation',
        'identifiers',
        'reporting_orgs',
        'elements',
        'codelists',
        'booleans',
        'dates',
        'faq',
    ]

@app.route('/<page_name>.html')
def basic_page(page_name):
    if page_name in basic_page_names:
        kwargs = {}
        if page_name.startswith('timeliness'):
            kwargs['timeliness'] = timeliness
            parent_page_name = 'timeliness'
        elif page_name.startswith('forwardlooking'):
            kwargs['forwardlooking'] = forwardlooking
            parent_page_name = 'forwardlooking'
        elif page_name.startswith('comprehensiveness'):
            kwargs['comprehensiveness'] = comprehensiveness
            parent_page_name = 'comprehensiveness'
        elif page_name.startswith('coverage'):
            kwargs['coverage'] = coverage
            parent_page_name = 'coverage'
        elif page_name.startswith('transparencyindicator'):
            kwargs['transparencyindicator'] = transparencyindicator
            parent_page_name = 'transparencyindicator'
        else:
            parent_page_name = page_name
        return render_template(page_name+'.html', page=parent_page_name, **kwargs)
    else:
        abort(404)

@app.route('/data/download_errors.json')
def download_errors_json():
    return  Response(json.dumps(current_stats['download_errors'], indent=2), mimetype='application/json'),

app.add_url_rule('/', 'index_redirect', lambda: redirect('index.html'))
app.add_url_rule('/licenses.html', 'licenses', licenses.main)
app.add_url_rule('/license/<license>.html', 'licenses_individual_license', licenses.individual_license)

@app.route('/publisher/<publisher>.html')
def publisher(publisher):
    publisher_stats = get_publisher_stats(publisher)
    budget_table = [ {
            'year': 'Total',
            'count_total': sum(sum(x.values()) for x in publisher_stats['count_budgets_by_type_by_year'].values()),
            'sum_total': { currency:sum(sums.values()) for by_currency in publisher_stats['sum_budgets_by_type_by_year'].values() for currency,sums in by_currency.items()  },
            'count_original': sum(publisher_stats['count_budgets_by_type_by_year']['1'].values()) if '1' in publisher_stats['count_budgets_by_type_by_year'] else None,
            'sum_original': { k:sum(v.values()) for k,v in publisher_stats['sum_budgets_by_type_by_year']['1'].items() } if '1' in publisher_stats['sum_budgets_by_type_by_year'] else None,
            'count_revised': sum(publisher_stats['count_budgets_by_type_by_year']['2'].values()) if '2' in publisher_stats['count_budgets_by_type_by_year'] else None,
            'sum_revised': { k:sum(v.values()) for k,v in publisher_stats['sum_budgets_by_type_by_year']['2'].items() } if '2' in publisher_stats['sum_budgets_by_type_by_year'] else None
        } ] + [
            {
                'year': year,
                'count_total': sum(x[year] for x in publisher_stats['count_budgets_by_type_by_year'].values() if year in x),
                'sum_total': { currency:sums.get(year) for by_currency in publisher_stats['sum_budgets_by_type_by_year'].values() for currency,sums in by_currency.items()  },
                'count_original': publisher_stats['count_budgets_by_type_by_year']['1'].get(year) if '1' in publisher_stats['count_budgets_by_type_by_year'] else None,
                'sum_original': { k:v.get(year) for k,v in publisher_stats['sum_budgets_by_type_by_year']['1'].items() } if '1' in publisher_stats['sum_budgets_by_type_by_year'] else None,
                'count_revised': publisher_stats['count_budgets_by_type_by_year']['2'].get(year) if '2' in publisher_stats['count_budgets_by_type_by_year'] else None,
                'sum_revised': { k:v.get(year) for k,v in publisher_stats['sum_budgets_by_type_by_year']['2'].items() } if '2' in publisher_stats['sum_budgets_by_type_by_year'] else None
            } for year in sorted(set(sum((x.keys() for x in publisher_stats['count_budgets_by_type_by_year'].values()), [])))
        ]
    return render_template('publisher.html',
        url=lambda x: '../'+x,
        publisher=publisher,
        publisher_stats=publisher_stats,
        publisher_inverted=get_publisher_stats(publisher, 'inverted-file'),
        publisher_licenses=licenses.licenses_for_publisher(publisher),
        budget_table=budget_table
        )

@app.route('/codelist/<major_version>/<slug>.html')
def codelist(major_version, slug):
    i = slugs['codelist'][major_version]['by_slug'][slug]
    element = current_stats['inverted_publisher']['codelist_values_by_major_version'][major_version].keys()[i]
    values = nested_dictinvert(current_stats['inverted_publisher']['codelist_values_by_major_version'][major_version].values()[i])
    return render_template('codelist.html',
        element=element,
        values=values,
        reverse_codelist_mapping={ major_version:dictinvert(mapping) for major_version, mapping in codelist_mapping.items() },
        url=lambda x: '../../'+x,
        major_version=major_version,
        page='codelists')

@app.route('/element/<slug>.html')
def element(slug):
    i = slugs['element']['by_slug'][slug]
    element = current_stats['inverted_publisher']['elements'].keys()[i]
    publishers = current_stats['inverted_publisher']['elements'].values()[i]
    file_grouped = current_stats['inverted_file_grouped']['elements'].values()[i]
    return render_template('element.html',
        element=element,
        publishers=publishers,
        file_grouped=file_grouped,
        url=lambda x: '../'+x,
        page='elements')


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
    return render_template('registration_agencies.html',
        page='registration_agencies',
        registration_agencies=registration_agencies,
        registration_agencies_publishers=registration_agencies_publishers,
        nonmatching=nonmatching)

# Server an image through the development server (--live)
@app.route('/<image>.png')
def image_development(image):
    return Response(open(os.path.join('out', image+'.png')).read(), mimetype='image/png')

@app.route('/<name>.csv')
def csv_development(name):
    return Response(open(os.path.join('out', name+'.csv')).read(), mimetype='text/csv')

@app.route('/publisher_imgs/<image>.png')
def image_development_publisher(image):
    print(image)
    return Response(open(os.path.join('out', 'publisher_imgs', image+'.png')).read(), mimetype='image/png')

if __name__ == '__main__':
    if '--live' in sys.argv:
        app.debug = True
        app.run()
    else:
        from flask_frozen import Freezer
        app.config['FREEZER_DESTINATION'] = 'out'
        app.config['FREEZER_REMOVE_EXTRA_FILES'] = False
        app.debug = False    # Comment to turn off debugging
        app.testing = True   # Comment to turn off debugging
        freezer = Freezer(app)

        @freezer.register_generator
        def url_generator():
            for page_name in basic_page_names:
                yield 'basic_page', {'page_name': page_name}
            for publisher in current_stats['inverted_publisher']['activities'].keys():
                yield 'publisher', {'publisher': publisher}
            for slug in slugs['element']['by_slug']:
                yield 'element', {'slug': slug}
            for major_version, codelist_slugs in slugs['codelist'].items():
                for slug in codelist_slugs['by_slug']:
                    yield 'codelist', {
                        'slug': slug,
                        'major_version': major_version
                    }
            for license in licenses.licenses:
                if license == None:
                    license = 'None'
                yield 'licenses_individual_license', {'license':license}


        freezer.freeze()
