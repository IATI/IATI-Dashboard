"""
Uses the CKAN API on the IATI Registry to fetch data about publishers
Makes a call to get a list of all organisations, then
grabs data about each individual publisher and stores the
information in one file per publisher.

We're particulary looking for information such as
name, organisation type, and the link back to the registry
"""

import requests
import os
import json

#Make a directory to save the data about each publisher
try:
    os.makedirs(os.path.join('data','ckan_publishers'))
except OSError:
    pass

page_size = 100
url = 'https://iatiregistry.org/api/3/action/organization_list'
params = {
    'all_fields': 'true',
    'include_extras': 'true',
    'include_tags': 'true',
    'include_groups': 'true',
    'include_users': 'true',
    'limit': page_size,
}

# Loop through the organisation list json, saving a file of information about each publisher
page = 0
while True:
    params['offset'] = page_size * page
    res = requests.get(url, params=params).json()['result']
    if res == []:
        break
    for publisher in res:
        name = publisher.get('name')
        output = {'result': publisher}
        with open(os.path.join('data', 'ckan_publishers', name + '.json'), 'w') as fp:
            _ = json.dump(output, fp)
    page += 1
