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

codelist_mapping = {x['path']:x['codelist'] for x in json.load(open('data/mapping.json'))}
# Perform the same transformation as https://github.com/IATI/IATI-Stats/blob/d622f8e88af4d33b1161f906ec1b53c63f2f0936/stats.py#L12
codelist_mapping = {re.sub('^\/\/iati-activity', './', k):v for k,v in codelist_mapping.items()}
codelist_mapping = {re.sub('^\/\/', './/', k):v for k,v, in codelist_mapping.items() }

codelist_sets = { cname:set(c['code'] for c in codelist['data']) for cname,codelist in JSONDir('data/IATI-Codelists/out/clv2/json/en/').items() }

import csv
from decimal import Decimal
dac2012 = {x[0]:Decimal(x[1].replace(',','')) for x in csv.reader(open('data/dac2012.csv'))}
