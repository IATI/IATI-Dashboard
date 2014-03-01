import os, json, re
from collections import defaultdict
from flask import render_template

isoDateRegex = re.compile('(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})')

def main():
    repos = json.load(open(os.path.join('data/github/repo.json')))
    github_stats = {
        'open_issues': sum([x['open_issues_count'] for x in repos]),
    }
    return render_template('github.html', github=True, github_overview=True, repos=repos, github_stats=github_stats)

def milestones():
    milestones_calendar = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    milestones_nodate = []
    no_milestone = {}
    no_open_issues = []

    for fname in os.listdir('data/github/milestones'):
        milestones = json.load(open(os.path.join('data/github/milestones',fname)))
        if not 'message' in milestones: #if GitHub API has returned a 'message' element at the beginning the json we won't have the data we want
            for milestone in milestones:
                milestone['repo'] = fname[:-5]
                if not milestone['due_on']:
                    milestones_nodate.append(milestone)
                else:
                    m = isoDateRegex.match(milestone['due_on'])
                    milestones_calendar[m.group(1)][m.group(2)][m.group(3)].append(milestone)
                    #print('   ', milestone['title'], '---', milestone['due_on'], '---', str(milestone['open_issues'])+'/'+str(milestone['closed_issues']))

    for fname in os.listdir('data/github/issues_no_milestone'):
        issues = json.load(open(os.path.join('data/github/issues_no_milestone',fname)))
        if type(issues) == list:
            if len(issues):
                no_milestone[fname[:-5]] = len(issues)
    
    for fname in os.listdir('data/github/no_open_issues'):
        no_open_issues.append(fname[:-5])
        

    return render_template('milestones.html', milestones_calendar=milestones_calendar, milestones_nodate=milestones_nodate, no_milestone=no_milestone, sorted=sorted, github=True, milestones=True, no_open_issues=no_open_issues)

def milestones_closed():
    milestones_closed_calendar = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    milestones_nodate = []

    for fname in os.listdir('data/github/milestones_closed'):
        milestones = json.load(open(os.path.join('data/github/milestones_closed',fname)))
        if not 'message' in milestones: #if GitHub API has returned a 'message' element at the beginning the json we won't have the data we want
            for milestone in milestones:
                milestone['repo'] = fname[:-5]
                if not milestone['due_on']:
                    milestones_nodate.append(milestone)
                else:
                    m = isoDateRegex.match(milestone['due_on'])
                    milestones_closed_calendar[m.group(1)][m.group(2)][m.group(3)].append(milestone)
                    #print('   ', milestone['title'], '---', milestone['due_on'], '---', str(milestone['open_issues'])+'/'+str(milestone['closed_issues']))
        

    return render_template('milestones-completed.html', milestones_closed_calendar=milestones_closed_calendar, milestones_nodate=milestones_nodate, sorted=sorted, github=True, milestones_completed=True)

