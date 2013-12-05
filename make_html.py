from collections import OrderedDict
import json
import jinja2


def validation(jinja_env):
    validation_template = jinja_env.get_template('validation.html')

    current_stats = {
        'aggregated': json.load(open('./stats-calculated/current/aggregated.json'), object_pairs_hook=OrderedDict),
        'inverted_file': json.load(open('./stats-calculated/current/inverted-file.json'), object_pairs_hook=OrderedDict)
    }
    ckan = json.load(open('./ckan.json'), object_pairs_hook=OrderedDict)
    return validation_template.render(current_stats=current_stats, ckan=ckan)



import github.web
urls = {
    'validation.html': validation,
    'github.html': github.web.main
}

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
jinja_env.filters['url_to_filename'] = lambda x: x.split('/')[-1]

for url, f in urls.items():
    with open('out/'+url, 'w') as fp:
        fp.write(f(jinja_env).encode('utf-8'))
