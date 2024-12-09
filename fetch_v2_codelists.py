import json
from os import makedirs
from os.path import join

import requests
from lxml import etree as ET

output_path = join(
    'data', 'IATI-Codelists-2', 'out', 'clv2', 'json', 'en')
makedirs(output_path)
resp = requests.get('https://codelists.codeforiati.org/api/')
codelists = resp.json()['formats']['json']['languages']['en']
for codelist_name, codelist_url in codelists.items():
    r = requests.get("http://dev.iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/" + codelist_url.split("/")[-1])
    if r.status_code == 404:
        continue
    codelist_json = r.json()
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
    'https://raw.githubusercontent.com/IATI/IATI-Codelists/version-2.03/mapping.xml',
    ]
#    'https://raw.githubusercontent.com/codeforIATI/Unofficial-Codelists/master/mapping.xml']
mappings = []
for mapping_url in mapping_urls:
    resp = requests.get(mapping_url)
    doc = ET.fromstring(resp.content)
    mappings += mapping_to_json(doc)

with open(join('data', 'IATI-Codelists-2', 'out', 'clv2', 'mapping.json'), 'w') as f:
    json.dump(sorted(mappings, key=lambda x: x['path']), f)
