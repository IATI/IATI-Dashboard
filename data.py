import json
from collections import OrderedDict, defaultdict
import sys, os, re, copy, datetime, unicodecsv
import UserDict

publisher_re = re.compile('(.*)\-[^\-]')

class GroupFiles(object, UserDict.DictMixin):
    def __init__(self, inputdict):
        self.inputdict = inputdict
        self.cache = {}

    def __getitem__(self, key):
        if key in self.cache: return self.cache[key]
        self.inputdict[key]
        out = OrderedDict()
        for k2,v2 in self.inputdict[key].items():
            if type(v2) == OrderedDict:
                out[k2] = OrderedDict()
                for listitem, v3 in v2.items():
                    m = publisher_re.match(listitem)
                    if m:
                        publisher = m.group(1)
                        if not publisher in out[k2]:
                            out[k2][publisher] = OrderedDict()
                        out[k2][publisher][listitem] = v3
                    else:
                        pass # FIXME
            else:
                out[k2] = v2
        self.cache[key] = out
        return out

class JSONDir(object, UserDict.DictMixin):
    def __init__(self, folder):
        self.folder = folder
        self.cache = {}

    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            if os.path.exists(os.path.join(self.folder, key)):
                value = JSONDir(os.path.join(self.folder, key))
            elif os.path.exists(os.path.join(self.folder, key+'.json')):
                with open(os.path.join(self.folder, key+'.json')) as fp:
                    value = json.load(fp, object_pairs_hook=OrderedDict)
            else:
                raise KeyError, key
            self.cache[key] = value
            return value

    def keys(self):
        return [ x[:-5] if x.endswith('.json') else x for x in os.listdir(self.folder) ]

    def __iter__(self):
        return iter(self.keys())

def get_publisher_stats(publisher, stats_type='aggregated'):
    try:
        return JSONDir('./stats-calculated/current/{0}-publisher/{1}'.format(stats_type, publisher))
    except IOError:
        return {}


current_stats = {
    'aggregated': JSONDir('./stats-calculated/current/aggregated'),
    'aggregated_file': JSONDir('./stats-calculated/current/aggregated-file'),
    'inverted_publisher': JSONDir('./stats-calculated/current/inverted-publisher'),
    'inverted_file': JSONDir('./stats-calculated/current/inverted-file'),
    'download_errors': []
}
current_stats['inverted_file_grouped'] = GroupFiles(current_stats['inverted_file'])
ckan_publishers = JSONDir('./data/ckan_publishers')
ckan = json.load(open('./stats-calculated/ckan.json'), object_pairs_hook=OrderedDict)
gitdate = json.load(open('./stats-calculated/gitdate.json'), object_pairs_hook=OrderedDict)
with open('./data/downloads/errors') as fp:
    for line in fp:
        if line != '.\n':
            current_stats['download_errors'].append(line.strip('\n').split(' ', 3))
data_tickets = defaultdict(list)
with open('./data/issues.csv') as fp:
    # Skip BOM
    fp.read(3)
    reader = unicodecsv.DictReader(fp)
    for issue in reader:
        data_tickets[issue['data_provider_regisrty_id']].append(issue)

def transform_codelist_mapping_keys(codelist_mapping):
    # Perform the same transformation as https://github.com/IATI/IATI-Stats/blob/d622f8e88af4d33b1161f906ec1b53c63f2f0936/stats.py#L12
    codelist_mapping = {k:v for k,v in codelist_mapping.items() if not k.startswith('//iati-organisation') }
    codelist_mapping = {re.sub('^\/\/iati-activity', './', k):v for k,v in codelist_mapping.items() }
    codelist_mapping = {re.sub('^\/\/', './/', k):v for k,v, in codelist_mapping.items() }
    return codelist_mapping

def create_codelist_mapping(major_version):
    codelist_mapping = {x['path']:x['codelist'] for x in json.load(open('data/IATI-Codelists-{}/out/clv2/mapping.json'.format(major_version)))}
    return transform_codelist_mapping_keys(codelist_mapping)

MAJOR_VERSIONS = ['1', '2']

codelist_mapping = { v:create_codelist_mapping(v) for v in MAJOR_VERSIONS }
codelist_conditions = { 
    major_version: transform_codelist_mapping_keys({ x['path']:x.get('condition') for x in json.load(open('data/IATI-Codelists-{}/out/clv2/mapping.json'.format(major_version)))})
    for major_version in MAJOR_VERSIONS }

codelist_sets = { 
    major_version: {
        cname:set(c['code'] for c in codelist['data']) for cname, codelist in JSONDir('data/IATI-Codelists-{}/out/clv2/json/en/'.format(major_version)).items()
    } for major_version in MAJOR_VERSIONS }


#Simple look up to map publisher id to a publishers given name (title)
publisher_name={publisher:publisher_json['result']['title'] for publisher,publisher_json in ckan_publishers.items()}
#Create a list of tuples ordered by publisher given name titles - this allows us to display lists of publishers in alphabetical order
publishers_ordered_by_title = [ (publisher_name[publisher],publisher) for publisher in current_stats['inverted_publisher']['activities'] ]
publishers_ordered_by_title.sort(key=lambda x: unicode.lower(x[0]))


import csv
from decimal import Decimal
try:
    dac2012 = {x[0]:Decimal(x[1].replace(',','')) for x in csv.reader(open('data/dac2012.csv'))}
except IOError:
    dac2012 = {}




def make_slugs(keys):
    out = {'by_slug':{}, 'by_i':{}}
    for i,key in enumerate(keys):
        slug = re.sub('[^a-zA-Z0-9:@\-_]', '', re.sub('{[^}]*}', '', key.replace('{http://www.w3.org/XML/1998/namespace}','xml:').replace('/','_'))).strip('_')
        while slug in out['by_slug']:
            slug += '_'
        out['by_slug'][slug] = i
        out['by_i'][i] = slug
    return out

slugs = {
    'codelist': { major_version:(
            make_slugs(current_stats['inverted_publisher']['codelist_values_by_major_version'][major_version].keys())
            if major_version in current_stats['inverted_publisher']['codelist_values_by_major_version']
            else make_slugs([])
        ) for major_version in MAJOR_VERSIONS },
    'element': make_slugs(current_stats['inverted_publisher']['elements'].keys())
}


