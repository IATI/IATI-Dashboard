import os, json, re
from collections import defaultdict
from flask import render_template

def main():
    isoDateRegex = re.compile('(-?[0-9]{4,})-([0-9]{2})-([0-9]{2})')

    milestones_calendar = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    milestones_nodate = []
    no_milestone = {}

    for fname in os.listdir('data/github/milestones'):
        milestones = json.load(open(os.path.join('data/github/milestones',fname)))
        if not 'message' in milestones:
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
        

    return render_template('github.html', milestones_calendar=milestones_calendar, milestones_nodate=milestones_nodate, no_milestone=no_milestone, sorted=sorted, github=True)

