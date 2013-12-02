from collections import OrderedDict
import json
import jinja2

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
jinja_env.filters['url_to_filename'] = lambda x: x.split('/')[-1]

validation_template = jinja_env.get_template('validation.html')

current_stats = {
    'aggregated': json.load(open('./stats-calculated/current/aggregated.json'), object_pairs_hook=OrderedDict),
    'inverted_file': json.load(open('./stats-calculated/current/inverted-file.json'), object_pairs_hook=OrderedDict)
}
ckan = json.load(open('./ckan.json'), object_pairs_hook=OrderedDict)


with open('out/validation.html', 'w') as fp:
    fp.write(validation_template.render(current_stats=current_stats, ckan=ckan).encode('utf-8'))

