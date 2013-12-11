from collections import OrderedDict
import json
import jinja2
import copy
import re

def group_files(d):
    out = OrderedDict()
    publisher_re = re.compile('(.*)\-[^\-]')
    for k,v in d.items():
        out[k] = OrderedDict()
        for k2,v2 in v.items():
            if type(v2) == list:
                out[k][k2] = OrderedDict()
                v2.sort()
                for listitem in v2:
                    publisher = publisher_re.match(listitem).group(1)
                    if not publisher in out[k][k2]:
                        out[k][k2][publisher] = []
                    out[k][k2][publisher].append(listitem)
            else:
                out[k][k2] = v2
    return out
            

current_stats = {
    'aggregated': json.load(open('./stats-calculated/current/aggregated.json'), object_pairs_hook=OrderedDict),
    'inverted': json.load(open('./stats-calculated/current/inverted.json'), object_pairs_hook=OrderedDict),
    'inverted_file': json.load(open('./stats-calculated/current/inverted-file.json'), object_pairs_hook=OrderedDict),
}
current_stats['inverted_file_grouped'] = group_files(current_stats['inverted_file'])
ckan = json.load(open('./stats-calculated/ckan.json'), object_pairs_hook=OrderedDict)

def template_page(template, **kwargs):
    def f(jinja_env):
        validation_template = jinja_env.get_template(template)
        return validation_template.render(sorted=sorted, **kwargs)
    return f

def iati_stats_page(template, **kwargs):
    return template_page(template, current_stats=current_stats, ckan=ckan, **kwargs) 

import github.web
urls = {
    'index.html': iati_stats_page('index.html'),
    'files.html': iati_stats_page('files.html', files=True),
    'validation.html': iati_stats_page('validation.html', validation=True),
    'versions.html': iati_stats_page('versions.html', versions=True),
    'licenses.html': iati_stats_page('licenses.html', licenses=True),
    'organisation.html': iati_stats_page('organisation.html', organisation=True),
    'elements.html': iati_stats_page('elements.html', elements=True),
    'github.html': github.web.main,
}

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
jinja_env.filters['url_to_filename'] = lambda x: x.split('/')[-1]

for url, f in urls.items():
    with open('out/'+url, 'w') as fp:
        fp.write(f(jinja_env).encode('utf-8'))
