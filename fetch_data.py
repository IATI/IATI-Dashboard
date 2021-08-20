"""
Uses the CKAN API on the IATI Registry to fetch data about publishers
Makes a call to get a list of all publishers, then
grabs data about each individual publisher and stores the
information in one file per publisher.

We're particulary looking for information such as
name, organisation type, and the link back to the registry
"""
from pathlib import Path
import os
import json
import time

import requests

# Make a directory to save the data about each publisher
os.makedirs(Path('data/ckan_publishers'), exist_ok=True)

page_size = 50
res = requests.get('https://iatiregistry.org/api/3/action/organization_list')
res.raise_for_status()
publisher_ids = res.json()['result']
url = 'https://iatiregistry.org/api/3/action/organization_show'

# Loop through the publisher list, saving a file of information about each publisher
for publisher_id in publisher_ids:
    res = requests.get(url, params={'id': publisher_id})
    time.sleep(0.1)
    res.raise_for_status()
    publisher = res.json()['result']
    name = publisher.get('name')
    output = {'result': publisher}
    with open(os.path.join('data', 'ckan_publishers', name + '.json'), 'w') as fp:
        _ = json.dump(output, fp)
