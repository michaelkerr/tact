# -*- coding: utf-8 -*-

import json
import csv
from datetime import datetime
from os import path
from pprint import pprint
import requests
#from jira import JIRA

from sys import exit
import yaml
from urllib import urlencode


### CONFIGURATION ###
config_file = path.join(path.dirname(path.realpath(__file__)), 'config/config.yml')
if path.exists(config_file):
    config = yaml.load(open(config_file, 'r'))
else:
    print config_file + ' not found'
    exit()

server = config['server']
credentials = {'uname': config['username'], 'pword': config['password']}
api_url = server + 'api/latest/'
search_url = api_url + 'search?'

headers = {'content-type': 'application/json;charset=UTF-8'}
out_file = "data_1.json"
out_file = "epic_data.json"


def search_issues(creds, url, data):
    params = {
        'jql': data,
        'maxResults': 250
        }

    try:
        response = requests.get(url, headers=headers, auth=(creds['uname'], creds['pword']), params=params)
        return response.json()
    except Exception as e:
        print e
        exit()


def get_changelog(creds, url, issue_key):
    query_url = url + 'issue/' + issue_key + '/changelog'
    try:
        response = requests.get(query_url, headers=headers, auth=(creds['uname'], creds['pword']))
        return response.json()
    except Exception as e:
        print e
        exit()



### MAIN ###
if __name__ == '__main__':
    #TODO Get the Project ID

    ##################################################
    # LOAD EXISTING DATA FROM DATA.json
    ##################################################
    try:
        with open(out_file, 'r') as infile:
            epic_data = json.load(infile)
    except Exception as e:
        epic_data = []

    existing_epics = []
    for issue in epic_data:
        existing_epics.append(issue['key'])

    ##################################################
    # GET ALL THE COMPLETED EPICS IN THE PROJECT
    ##################################################
    print "Getting Epics....."
    epic_search_data = 'project = ID AND issuetype = Epic AND status = Done AND (Labels not in ("exclude") or labels is EMPTY)'
    epics = search_issues(credentials, search_url, epic_search_data)
    print "Done."

    # FOR EACH EPIC (FEATURE)
    for epic in epics['issues']:
        ##################################################
        # FOR EACH EPIC - GET THE START DATE(S) [LIST], END DATE(S) [LIST]
        ##################################################

        if (epic['key'] not in existing_epics):
            print "Processing Epic: " + str(epic['key'])

            changelog = get_changelog(credentials, api_url, epic['key'])

            epic_dates = {
                'key': epic['key'],
                'start': [],
                'done': [],
                'issues': []
                }

            for entry in changelog['values']:
                for item in entry['items']:
                    if item['field'] == 'status' and item['toString'] == 'In Progress':
                        epic_dates['start'].append(entry['created'].split('T')[0])
                    elif item['field'] == 'status' and item['toString'] == 'Done':
                        epic_dates['done'].append(entry['created'].split('T')[0])

            #TODO DONT ADD IF END DATE IS EMPTY

            if len(epic_dates['start']) != 0 and len(epic_dates['done']) !=0:
                ##################################################
                #GET THE LIST OF ALL THE ISSUES IN THE EPICS [TASKS, STORIES, ETC (NOT BUGS, DESIGN TASKS)]
                ##################################################
                issue_search_data = '"Epic Link" = %s and issuetype not in (Bug, "Design Task")' % (epic['key'])
                issues = search_issues(credentials, search_url, issue_search_data)

                ##################################################
                #FOR EACH ISSUE IN THE EPIC - GET THE DATES
                #TODO
                ##################################################
                issue_data = []
                print "Parsing issues"
                for issue in issues['issues']:
                    changelog = get_changelog(credentials, api_url, issue['key'])

                    issue_dates = {
                        'key': epic['key'],
                        'start': [],
                        'done': []
                        }

                    for entry in changelog['values']:
                        for item in entry['items']:
                            if item['field'] == 'status' and item['toString'] == 'In Progress':
                                issue_dates['start'].append(entry['created'].split('T')[0])
                            elif item['field'] == 'status' and item['toString'] == 'Done':
                                issue_dates['done'].append(entry['created'].split('T')[0])

                    #ADD THE ISSUE DATES TO THE EPIC ISSUE LIST
                    if len(issue_dates['start']) != 0:
                        epic_dates['issues'].append(issue_dates)
                    if issue_dates['start'] == 0:
                        print issue_dates['key']

                epic_data.append(epic_dates)
                pprint(epic_dates)
            else:
                print "No start date.  Skipping"

    with open(out_file, 'w') as outfile:
        json.dump(epic_data, outfile)

'''
Output format:
{
	"start": ["YYYY-MM-DD"],
	"done": ["YYYY-MM-DD"],
	"issues": [
	  {
		"start": ["YYYY-MM-DD"],
		"done": ["YYYY-MM-DD"],
		"key": "<PROJECT>-<###...#>"}
	],
	"key": "<PROJECT>-<###...#>"
  }
 '''
