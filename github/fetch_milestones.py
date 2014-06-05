import json
import requests
import os
from requests.auth import HTTPBasicAuth
from config import user,password

def fetch():
    try:
        os.makedirs(os.path.join('data','github','milestones_closed'))
        os.makedirs(os.path.join('data','github','no_open_issues'))
        os.makedirs(os.path.join('data','github','issues_no_milestone'))
        os.makedirs(os.path.join('data','github','milestones'))
    except IOError:
        pass
    except OSError:
        pass

    r = requests.get('https://api.github.com/orgs/IATI/repos',auth=HTTPBasicAuth(user,password))
    with open('data/github/repo.json', 'w') as fp:
        fp.write(r.text.encode('utf-8'))
    for repo in json.loads(r.text):
        milestones_url = repo['milestones_url'].replace('{/number}','')
        milestones_request = requests.get(milestones_url,auth=HTTPBasicAuth(user,password))
        with open('data/github/milestones/{0}.json'.format(repo['name']), 'w') as fp:
            fp.write(milestones_request.text.encode('utf-8'))

        issues_url = repo['issues_url'].replace('{/number}','')
        issues_no_milestone_request = requests.get(issues_url, params={'milestone':'none'},auth=HTTPBasicAuth(user,password))
        with open('data/github/issues_no_milestone/{0}.json'.format(repo['name']), 'w') as fp:
            fp.write(issues_no_milestone_request.text.encode('utf-8'))
        
        open_issues = repo['open_issues']
        if open_issues == 0:
            with open('data/github/no_open_issues/{0}.json'.format(repo['name']), 'w') as fp:
                fp.write('0')
     
        milestones_closed_url = repo['milestones_url'].replace('{/number}','') + '?state=closed'
        milestones_request = requests.get(milestones_closed_url,auth=HTTPBasicAuth(user,password))
        with open('data/github/milestones_closed/{0}.json'.format(repo['name']), 'w') as fp:
        #with open('data/github/milestones_closed/urls') as fp:
            fp.write(milestones_request.text.encode('utf-8'))
            #fp.write(milestones_closed_url)


if __name__ == '__main__':
    fetch()
