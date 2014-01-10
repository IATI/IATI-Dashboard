import json
import requests
import os

def fetch():
    try:
        os.makedirs(os.path.join('data','github','issues_no_milestone'))
        os.makedirs(os.path.join('data','github','milestones'))
    except IOError:
        pass
    except OSError:
        pass

    r = requests.get('https://api.github.com/orgs/IATI/repos')
    for repo in json.loads(r.text):
        milestones_url = repo['milestones_url'].replace('{/number}','')
        milestones_request = requests.get(milestones_url)
        with open('data/github/milestones/{0}.json'.format(repo['name']), 'w') as fp:
            fp.write(milestones_request.text)

        issues_url = repo['issues_url'].replace('{/number}','')
        issues_no_milestone_request = requests.get(issues_url, params={'milestone':'none'})
        with open('data/github/issues_no_milestone/{0}.json'.format(repo['name']), 'w') as fp:
            fp.write(issues_no_milestone_request.text)

if __name__ == '__main__':
    fetch()
