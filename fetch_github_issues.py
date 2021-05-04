"""
Fetch codeforIATI/iati-data-bugtracker github issues
"""
from pathlib import Path
from collections import defaultdict
import os
import json

import requests

# Make a directory to save github issue data
os.makedirs(Path('data/github/publishers'), exist_ok=True)

j = requests.get(
    'https://api.github.com/repos/codeforIATI/iati-data-bugtracker/issues',
    params={'per_page': 100, 'state': 'open'}).json()
with open('data/github/issues.json', 'w') as fp:
    json.dump(j, fp)

publishers = defaultdict(list)
with open(Path('data/github/issues.json')) as f:
    issues = json.load(f)
for issue in issues:
    awaiting_triage = [
        l for l in issue['labels']
        if l['name'] == 'awaiting triage']
    if awaiting_triage:
        # ignore these
        continue
    pub_ids = [
        x['name'].split(': ', 1)[1]
        for x in issue['labels']
        if x['name'].startswith('publisher: ')]
    for pub_id in pub_ids:
        publishers[pub_id].append({
            'title': issue['title'],
            'html_url': issue['html_url'],
            'created_at': issue['created_at'],
            'updated_at': issue['updated_at'],
            'state': issue['state'],
            'labels': [l for l in issue['labels'] if not l['name'].startswith('publisher: ')],
        })
for pub_id, issues in publishers.items():
    with open(Path(f'data/github/publishers/{pub_id}.json'), 'w') as f:
        json.dump(issues, f)
