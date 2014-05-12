#import github.fetch_milestones
#github.fetch_milestones.fetch()

import requests
import os

r = requests.get('http://iatiregistry.org/api/3/action/organization_list')

try:
    os.makedirs(os.path.join('data','ckan_publishers'))
except OSError:
    pass

for publisher in r.json()['result']:
    r2 = requests.get('http://iatiregistry.org/api/3/action/organization_show', params={'id':publisher}) 
    with open(os.path.join('data', 'ckan_publishers', publisher+'.json'), 'w') as fp:
        fp.write(r2.text)
