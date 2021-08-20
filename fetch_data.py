"""
Uses the CKAN API on the IATI Registry to fetch data about publishers
Makes a call to get a list of all publishers, then
grabs data about each individual publisher and stores the
information in one file per publisher.

We're particulary looking for information such as
name, organisation type, and the link back to the registry
"""
from pathlib import Path
from os.path import join
from os import makedirs
import json

import requests

# Make a directory to save the data about each publisher
output_path = Path('data/ckan_publishers')
makedirs(output_path, exist_ok=True)

res = requests.get('https://registry.codeforiati.org/publisher_list.json')
res.raise_for_status()
publishers = res.json()['result']

# Loop through the publisher list, saving a file of information about each publisher
for publisher in publishers:
    name = publisher.get('name')
    output = {'result': publisher}
    with open(join(output_path, name + '.json'), 'w') as fp:
        _ = json.dump(output, fp)
