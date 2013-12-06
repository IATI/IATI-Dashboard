import json
import requests
import os

def fetch():
    try:
        os.makedirs(os.path.join('data','github','milestones'))
    except IOError:
        pass
    except OSError:
        pass

    r = requests.get('https://api.github.com/orgs/IATI/repos')
    for repo in json.loads(r.text):
        milestones_url = repo['milestones_url'].replace('{/number}','')
        r2 = requests.get(milestones_url)
        with open('data/{0}.json'.format(repo['name']), 'w') as fp:
            fp.write(r2.text)

if __name__ == '__main__':
    fetch()
