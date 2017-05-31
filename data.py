import json
from collections import OrderedDict, defaultdict
import sys, os, re, copy, datetime, unicodecsv
import UserDict
import csv

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

def JSONDir_to_memory(JSONDir_obj):
    """Copies data from a JSONDir object to an in-memory OrderedDict.
       Use sparingly due to the memory that copying publisher data consumes!
    Input: JSONDir_obj - a JSONDir object
    Returns: An in-memory OrderedDict
    """

    output_data = OrderedDict()

    # Loop over data within the JSONDir_obj and add to output data
    for publisher, agg in JSONDir_obj.items():
        output_data_sub = OrderedDict()
        for k,v in agg.items():
           output_data_sub.update({k: v})
        output_data.update({publisher: output_data_sub})

    return output_data


class JSONDir(object, UserDict.DictMixin):
    """Produces an object, to be used to access JSON-formatted publisher data and return
       this as an ordered dictionary (with nested dictionaries, if appropriate).
       Use of this class removes the need to load large amounts of data into memory.
    """

    def __init__(self, folder):
        """Set the path of the folder being accessed as an attribute to an instance of
           the object.
        """
        self.folder = folder

    def __getitem__(self, key):
        """Define how variables are gathered from the raw JSON files and then parsed into
           the OrderedDict that will be returned.

           Note:
            try-except should be used around file operations rather than checking before-hand
        """

        if os.path.exists(os.path.join(self.folder, key)):
            # The data being sought is a directory
            data = JSONDir(os.path.join(self.folder, key))
        elif os.path.exists(os.path.join(self.folder, key+'.json')):
            # The data being sought is a json file
            with open(os.path.join(self.folder, key+'.json')) as fp:
                data = json.load(fp, object_pairs_hook=OrderedDict)

            # Deal with publishers who had an old registry ID
            # If this publisher had at least one old ID in the past
            if (self.get_publisher_name() in get_registry_id_matches().values()) and ('gitaggregate' in self.folder):
                # Perform the merging
                # Look over the set of changed registry IDs
                for previous_id, current_id in get_registry_id_matches().items():
                    previous_path = os.path.join(folder.replace(current_id,previous_id), key+'.json')
                    #  If this publisher has had an old ID and there is data for it
                    if (current_id == self.get_publisher_name()) and os.path.exists(previous_path):
                        folder = self.folder
                        # Get the corresponding value for the old publisher ID, and merge with the existing value for this publisher
                        with open(previous_path) as old_fp:
                            old_pub_data = json.load(old_fp, object_pairs_hook=OrderedDict)
                            deep_merge(data, old_pub_data)
                            # FIXME i) Should deep_merge attempt to sort this ordereddict ii) Should there be an attempt to aggregate/average conflicting values?
        else:
            # No value found as either a folder or json file
            raise KeyError, key

        return data

    def keys(self):
        """Method to return a list of keys that are contained within the data folder that
           is being accessed within this instance.
        """
        return [ x[:-5] if x.endswith('.json') else x for x in os.listdir(self.folder) ]

    def __iter__(self):
        """Custom iterable, to iterate over the keys that are contained within the data
        folder that is being accessed within this instance.
        """
        return iter(self.keys())

    def get_publisher_name(self):
        """Find the name of the publisher that this data relates to.
           Note, this is a super hacky way to do this, prize available if a better way is found to do this!
        """

        # Get a list of the parts that are contained within this filepath
        path = os.path.normpath(self.folder)
        path_components = path.split(os.sep)

        # Loop over this list and return the publisher name if it is found within the historic list of publishers
        for x in path_components:
            if x in JSONDir('./stats-calculated/gitaggregate-publisher-dated').keys():
                return x

        # If got to the end of the loop and nothing found, this folder does not relate to a single publisher
        return None



def get_publisher_stats(publisher, stats_type='aggregated'):
    """Function to obtain current data for a given publisher.
    Returns: A JSONDir object for the publisher, or an empty dictionary if the publisher
             is not found.
    """
    try:
        return JSONDir('./stats-calculated/current/{0}-publisher/{1}'.format(stats_type, publisher))
    except IOError:
        return {}


def get_registry_id_matches():
    """Returns a dictionary of publishers who have modified their registry ID
    Returns: Dictionary, where the key is the old registry ID, and the corresponding
             value is the registry ID that data should be mapped to
    """

    # Load registry IDs for publishers who have changed their registry ID
    reader = csv.DictReader(open('registry_id_relationships.csv', 'rU'), delimiter=',')

    # Load this data into a dictonary
    registry_matches = {}
    for row in reader:
        registry_matches[row['previous_registry_id']] = row['current_registry_id']

    return registry_matches


def deep_merge(obj1, obj2):
    """Merges two OrderedDict objects with an unknown number of nested levels
    Input: obj1 - OrderedDict to be used as the base object
    Input: obj2 - OrderedDict to be merged into obj1
    Returns: Nothing, but obj1 will contain the full data
    """

    # Iterate through keys
    for key in obj1:
        # If this is value, we've hit the bottom, copy all of obj2 into obj1
        if type(obj1[key]) is not OrderedDict:
            for key2 in obj2:
                # If there exists a dict at that key, make sure it's not erased
                if key2 in obj1:
                    if type(obj1[key2]) is not OrderedDict:
                        # You can change behavior here to determine
                        # How duplicate keys are handled
                        obj1[key2] = obj2[key2]
                else:
                    obj1[key2] = obj2[key2]

        # If it's a dictionary we need to go deeper, by running this function recursively
        else:
            if key in obj2:
                deep_merge(obj1[key],obj2[key])


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

# Create a big dictionary of all codelist values by version and codelist name
codelist_sets = {
    major_version: {
        cname:set(c['code'] for c in codelist['data']) for cname, codelist in JSONDir('data/IATI-Codelists-{}/out/clv2/json/en/'.format(major_version)).items()
    } for major_version in MAJOR_VERSIONS }


#Simple look up to map publisher id to a publishers given name (title)
publisher_name={publisher:publisher_json['result']['title'] for publisher,publisher_json in ckan_publishers.items()}
#Create a list of tuples ordered by publisher given name titles - this allows us to display lists of publishers in alphabetical order
publishers_ordered_by_title = [ (publisher_name[publisher],publisher) for publisher in current_stats['inverted_publisher']['activities'] ]
publishers_ordered_by_title.sort(key=lambda x: unicode.lower(x[0]))

# List of publishers who report all their activities as a secondary publisher
secondary_publishers = [publisher for publisher, stats in JSONDir('./stats-calculated/current/aggregated-publisher').items()
                         if int(stats['activities']) == len(stats['activities_secondary_reported'])
                            and int(stats['activities']) > 0]

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
