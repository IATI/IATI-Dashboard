import sys, os, re
import subprocess
import urllib

from flask import Flask, render_template, redirect, Response
app = Flask(__name__)

from data import *

def dataset_to_publisher(publisher_slug):
    """ Converts a dataset (package) slug e.g. dfid-bd to the corresponding publisher
    slug e.g. dfid """
    return publisher_slug.rsplit('-',1)[0]

def iati_stats_page(template, **kwargs):
    def f():
        return render_template(template,
            current_stats=current_stats,
            ckan=ckan,
            publisher_name={p['name']:p['title'] for p in ckan_publishers['result']},
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
app.jinja_env.globals['stats_url'] = 'http://arstneio.com/iati/stats'
#app.jinja_env.globals['stats_url'] = 'http://localhost:8001'
app.jinja_env.globals['sorted'] = sorted
app.jinja_env.globals['enumerate'] = enumerate

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
}

app.route('/')(lambda: redirect('index.html'))

@app.route('/publisher/<publisher>.html')
def publisher(publisher):
    return iati_stats_page('publisher.html',
        url=lambda x: '../'+x,
        publisher=publisher,
        publisher_stats=get_publisher_stats(publisher),
        publisher_inverted=get_publisher_stats(publisher, 'inverted-file'),
        licenses=licenses.licenses_for_publisher(publisher)
        )()

@app.route('/codelist/<int:i>.html')
def codelist(i):
    element = current_stats['inverted_publisher']['codelist_values'].keys()[i]
    values = current_stats['inverted_publisher']['codelist_values'].values()[i]
    return iati_stats_page('codelist.html',
        element=element,
        values=values,
        codelist_mapping=codelist_mapping,
        url=lambda x: '../'+x,
        codelists=True)()

@app.route('/element/<int:i>.html')
def element(i):
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
            for publisher in ckan:
                yield 'publisher', {'publisher':publisher}
            for i in range(0, len(current_stats['inverted_publisher']['elements'])): 
                yield 'element', {'i':i}
            for i in range(0, len(current_stats['inverted_publisher']['codelist_values'])): 
                yield 'codelist', {'i':i}
            for license in licenses.licenses: 
                if license == None:
                    license = 'None'
                yield 'individual_license', {'license':license}
            

        freezer.freeze()
