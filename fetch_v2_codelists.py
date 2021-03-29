from os.path import join
from os import makedirs
import json

import requests
from lxml import etree as ET


output_path = join(
    'data', 'IATI-Codelists-2', 'out', 'clv2', 'json', 'en')
makedirs(output_path)
resp = requests.get('https://codelists.codeforiati.org/api/')
codelists = resp.json()['formats']['json']['languages']['en']
for codelist_name, codelist_url in codelists.items():
    codelist_json = requests.get(codelist_url).json()
    with open(join(output_path, codelist_name + '.json'), 'w') as f:
        json.dump(codelist_json, f)


def mapping_to_json(mappings):
    for mapping in mappings.xpath('//mapping'):
        out = {
            'path': mapping.find('path').text,
            'codelist': mapping.find('codelist').attrib['ref']
        }
        if mapping.find('condition') is not None:
            out['condition'] = mapping.find('condition').text
        yield out


mapping_urls = [
    'https://raw.githubusercontent.com/andylolz/IATI-Codelists/version-2.03/mapping.xml',
    'https://raw.githubusercontent.com/codeforIATI/Unofficial-Codelists/master/mapping.xml']
mappings = []
for mapping_url in mapping_urls:
    resp = requests.get(mapping_url)
    doc = ET.fromstring(resp.content)
    mappings += mapping_to_json(doc)

with open(join('data', 'IATI-Codelists-2', 'out', 'clv2', 'mapping.json'), 'w') as f:
    json.dump(sorted(mappings, key=lambda x: x['path']), f)
