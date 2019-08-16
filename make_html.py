# Script to generate static HTML pages
# This uses Jinja templating to render the HTML templates in the 'templates' folder
# Data is based on the files in the 'stats-calculated' folder, and extra logic in other files in this repository

from __future__ import print_function
import argparse
import os
import re
import subprocess
from collections import defaultdict
import timeliness
import forwardlooking
import comprehensiveness
import coverage
import summary_stats
import humanitarian
from vars import expected_versions
import text
import datetime
from flask import Flask, render_template, abort, Response
app = Flask(__name__, template_folder="static/templates")

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
        return 'http://iatistandard.org/organisation-standard/iati-organisations/'+path.split('@')[0]
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

# Store data processing times
date_time_data_str = max(gitdate.values())
date_time_data_obj = datetime.datetime.strptime(date_time_data_str[:19], '%Y-%m-%d %H:%M:%S') # Ignores timezone as this is unhelpful for user output

# Custom Jinja filters
app.jinja_env.filters['xpath_to_url'] = xpath_to_url
app.jinja_env.filters['url_to_filename'] = lambda x: x.split('/')[-1]
app.jinja_env.filters['dataset_to_publisher'] = dataset_to_publisher
app.jinja_env.filters['has_future_transactions'] = timeliness.has_future_transactions

# Custom Jinja globals
app.jinja_env.globals['url'] = lambda x: x
app.jinja_env.globals['datetime_generated'] = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %z']).strip()
app.jinja_env.globals['datetime_data'] = date_time_data_str
app.jinja_env.globals['datetime_data_homepage'] = date_time_data_obj.strftime('%d %B %Y (at %H:%M)')
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
app.jinja_env.globals['navigation_reverse'] = {page: k for k, pages in text.navigation.items() for page in pages}
app.jinja_env.globals['navigation_reverse'].update({k: k for k in text.navigation})
app.jinja_env.globals['current_stats'] = current_stats
app.jinja_env.globals['ckan'] = ckan
app.jinja_env.globals['ckan_publishers'] = ckan_publishers
app.jinja_env.globals['publisher_name'] = publisher_name
app.jinja_env.globals['publishers_ordered_by_title'] = publishers_ordered_by_title
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
    'publishing_stats',
    'timeliness',
    'timeliness_timelag',
    'forwardlooking',
    'comprehensiveness',
    'comprehensiveness_core',
    'comprehensiveness_financials',
    'comprehensiveness_valueadded',
    'coverage',
    'summary_stats',
    'humanitarian',
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
        elif page_name.startswith('summary_stats'):
            kwargs['summary_stats'] = summary_stats
            parent_page_name = 'summary_stats'
        elif page_name.startswith('humanitarian'):
            kwargs['humanitarian'] = humanitarian
            parent_page_name = 'humanitarian'
        else:
            parent_page_name = page_name
        return render_template(page_name + '.html', page=parent_page_name, **kwargs)
    else:
        abort(404)

# app.add_url_rule('/', 'index_redirect', lambda: redirect('index.html'))


# Server an image through the development server (--live)
@app.route('/<image>.png')
def image_development(image):
    return Response(open(os.path.join('out', image + '.png')).read(), mimetype='image/png')

@app.route('/<name>.csv')
def csv_development(name):
    return Response(open(os.path.join('out', name + '.csv')).read(), mimetype='text/csv')

@app.route('/publisher_imgs/<image>.png')
def image_development_publisher(image):
    print(image)
    return Response(open(os.path.join('out', 'publisher_imgs', image + '.png')).read(), mimetype='image/png')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",
                        help="Link to connect publishing stats to dashboard",
                        default="")
    args = parser.parse_args()
    app.jinja_env.globals['dashboard_url'] = args.url
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

    freezer.freeze()
