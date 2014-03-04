import json
from collections import OrderedDict, defaultdict
import sys, os, re, copy, datetime, unicodecsv

def group_files(d):
    out = OrderedDict()
    publisher_re = re.compile('(.*)\-[^\-]')
    for k,v in d.items():
        out[k] = OrderedDict()
        for k2,v2 in v.items():
            if type(v2) == OrderedDict:
                out[k][k2] = OrderedDict()
                for listitem, v3 in v2.items():
                    m = publisher_re.match(listitem)
                    if m:
                        publisher = m.group(1)
                        if not publisher in out[k][k2]:
                            out[k][k2][publisher] = OrderedDict()
                        out[k][k2][publisher][listitem] = v3
                    else:
                        pass # FIXME
            else:
                out[k][k2] = v2
    return out

def get_publisher_stats(publisher, stats_type='aggregated'):
    try:
        return json.load(open('./stats-calculated/current/{0}-publisher/{1}.json'.format(stats_type, publisher)), object_pairs_hook=OrderedDict)
    except IOError:
        return {}


current_stats = {
    'aggregated': json.load(open('./stats-calculated/current/aggregated.json'), object_pairs_hook=OrderedDict),
    'inverted_publisher': json.load(open('./stats-calculated/current/inverted-publisher.json'), object_pairs_hook=OrderedDict),
    'inverted_file': json.load(open('./stats-calculated/current/inverted-file.json'), object_pairs_hook=OrderedDict),
    'download_errors': []
}
current_stats['inverted_file_grouped'] = group_files(current_stats['inverted_file'])
ckan_publishers = json.load(open('./data/ckan_publishers.json'), object_pairs_hook=OrderedDict)
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
