"""
Uses the CKAN API on the IATI Registry to fetch data about publishers
Makes a call to get a list of all organisations, then
grabs data about each individual publisher and stores the 
information in one file per publisher.

We're particulary looking for information such as 
name, organisation type, and the link back to the registry

Once this is done we also fetch information about the IATI GitHub organisation's
issue milestone data
"""

import requests
import os

# Fetch a list of all organisations - returns json
r = requests.get('http://iatiregistry.org/api/3/action/organization_list')

#Make a directory to save the data about each publisher
try:
    os.makedirs(os.path.join('data','ckan_publishers'))
except OSError:
    pass

# Loop through the organisation list json, saving a file of information about each publisher
for publisher in r.json()['result']:
    r2 = requests.get('http://iatiregistry.org/api/3/action/organization_show', params={'id':publisher}) 
    with open(os.path.join('data', 'ckan_publishers', publisher+'.json'), 'w') as fp:
        fp.write(r2.text)



# Fetch information about the IATI GitHub organisation's issue milestone data
import github.fetch_milestones
github.fetch_milestones.fetch()

