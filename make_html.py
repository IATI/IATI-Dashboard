import sys, os, re
import subprocess
import urllib

from flask import Flask, render_template, redirect, Response
app = Flask(__name__)

print 'Doing initial data import'
from data import *
print 'Initial data import finished'

def dataset_to_publisher(publisher_slug):
    """ Converts a dataset (package) slug e.g. dfid-bd to the corresponding publisher
    slug e.g. dfid """
    return publisher_slug.rsplit('-',1)[0]

def iati_stats_page(template, **kwargs):
    def f():
        return render_template(template,
            current_stats=current_stats,
            ckan=ckan,
            publisher_name={publisher:publisher_json['result']['title'] for publisher,publisher_json in ckan_publishers.items()},
            data_tickets=data_tickets,
            **kwargs) 
    return f

def firstint(s):
    if s[0].startswith('<'): return 0
    m = re.search('\d+', s[0])
    return int(m.group(0))


app.jinja_env.filters['url_to_filename'] = lambda x: x.split('/')[-1]
app.jinja_env.filters['dataset_to_publisher'] = dataset_to_publisher
app.jinja_env.globals['url'] = lambda x: x
app.jinja_env.globals['datetime_generated'] = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %z']).strip()
app.jinja_env.globals['datetime_data'] = max(gitdate.values())
app.jinja_env.globals['stats_url'] = 'http://dashboard.iatistandard.org/stats'
#app.jinja_env.globals['stats_url'] = 'http://localhost:8001'
app.jinja_env.globals['sorted'] = sorted
app.jinja_env.globals['enumerate'] = enumerate

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
    'index.html': iati_stats_page('index.html', index=True, get_publisher_stats=get_publisher_stats),
    'publishers.html': iati_stats_page('publishers.html', publisher=True, get_publisher_stats=get_publisher_stats),
    'files.html': iati_stats_page('files.html', files=True, firstint=firstint),
    'download.html': iati_stats_page('download.html', download=True),
    'xml.html': iati_stats_page('xml.html', xml=True),
    'validation.html': iati_stats_page('validation.html', validation=True),
    'versions.html': iati_stats_page('versions.html', versions=True, expected_versions=expected_versions),
    'licenses.html': licenses.main,
    'organisation.html': iati_stats_page('organisation.html', organisation=True),
    'elements.html': iati_stats_page('elements.html', elements=True),
    'codelists.html': iati_stats_page('codelists.html', codelists=True, codelist_mapping=codelist_mapping),
    'booleans.html': iati_stats_page('booleans.html', booleans=True),
    'data/download_errors.json': lambda: Response(json.dumps(current_stats['download_errors'], indent=2), mimetype='application/json'),
    'github.html': github.web.main,
    'milestones.html': github.web.milestones,
    'milestones-completed.html': github.web.milestones_closed,
}

app.route('/')(lambda: redirect('index.html'))

@app.route('/publisher/<publisher>.html')
def publisher(publisher):
    return iati_stats_page('publisher.html',
        url=lambda x: '../'+x,
        publisher=publisher,
        publisher_stats=get_publisher_stats(publisher),
        publisher_inverted=get_publisher_stats(publisher, 'inverted-file'),
        publisher_licenses=licenses.licenses_for_publisher(publisher)
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
        url=lambda x: '../'+x,
        codelists=True)()

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
        get_publisher_stats=get_publisher_stats,
        url=lambda x: '../'+x,
        elements=True)()

app.route('/license/<license>.html')(licenses.individual_license)

def make_html(urls, outdir=''):
    for url, f in urls.items():
        full_url = outdir+'/'+url
        if callable(f):
            f.__name__ = full_url.replace('.','_').encode('utf-8')
            app.add_url_rule(full_url, view_func=f)
        else:
            make_html(f, full_url)

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
