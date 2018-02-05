# -*- coding: utf-8 -*-

from datetime import datetime
import json
import numpy as np
from pprint import pprint
from sys import exit

today = datetime.now()

in_file = "epic_data.json"
out_file = "data_2.json"
data_file = "takt_times.json"

def get_date(issue):
    #TODO
    return


def get_duration(start_date, end_date):
    return (end_date - start_date).days


def duration_list(data):
    numbers = []
    for entry in data:
        numbers.append(entry['metrics']['duration'])
    return numbers


def moving_average(data, n=3) :
    ret = np.cumsum(data, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def sort_done(data):
    data_dict = {}
    for entry in data:
        data_dict[entry['done']] = entry['metrics']['duration']
    return data_dict



### MAIN ###
if __name__ == '__main__':
    #GET THE FEATURE DATA
    try:
        with open(in_file, 'r') as infile:
            epic_data = json.load(infile)
    except Exception as e:
        print e

    processed_data = []
    takt_data = []

    new_epic_data = []

    for epic in epic_data:
        epic_dict = {
            'delivery': [] #list of datetime objects
        }

        #TODO move to get_date()
        epic_start = datetime.strptime(str(epic['start'][0]), "%Y-%m-%d")

        if len(epic['start']) > 1:
            for start_date in epic['start']:
                start_date = datetime.strptime(str(start_date), "%Y-%m-%d")
                if start_date < epic_start:
                    epic_start = datetime.strptime(str(start_date), "%Y-%m-%d")

        epic_dict['start'] = epic_start

        #TODO move to get_date()
        epic_done = datetime.strptime(str(epic['done'][0]), "%Y-%m-%d")

        if len(epic['done']) > 1:
            for done_date in epic['done']:
                done_date = datetime.strptime(str(done_date), "%Y-%m-%d")
                if done_date < epic_done:
                    epic_done = datetime.strptime(str(done_date), "%Y-%m-%d")

        epic_dict['done'] = epic_done

        ##################################################
        # Add the delivery dates of the issues, correct Epic start/end if req'd
        ##################################################
        for issue in epic['issues']:
            if len(issue['done']) > 0:
                epic_dict['delivery'].append(datetime.strptime(str(issue['done'][0]), "%Y-%m-%d"))

                # If the delivery date is before the epic start, update epic_dict['start']
                if get_duration(epic_dict['start'], datetime.strptime(str(issue['done'][0]), "%Y-%m-%d")) < 0:
                    epic_dict['start'] = datetime.strptime(str(issue['done'][0]), "%Y-%m-%d")

                # If the delivery date is after the epic end, update epic_dict['done']
                if get_duration(datetime.strptime(str(issue['done'][0]), "%Y-%m-%d"), epic_dict['done']) < 0:
                    epic_dict['done'] = datetime.strptime(str(issue['done'][0]), "%Y-%m-%d")
            else:
                print issue['done'], epic_done
        # Sort the delivery list in order of completion
        epic_dict['delivery'] = sorted(epic_dict['delivery'], key=lambda x: x)

        ##################################################
        # "Takt" delivery time
        ##################################################
        takt_list = []
        start_date = epic_dict['start']
        last = 0

        for done_date in sorted(epic_dict['delivery'], key=lambda x: x):
            duration = get_duration(start_date, done_date)
            if duration == 0:
                duration = last
            start_date = done_date
            last = duration
            takt_list.append(duration)

        if len(takt_list) > 1 and not all(v == 0 for v in takt_list):
            processed_data.append(takt_list)

            temp_epic_dict = {}
            temp_epic_dict['key'] = epic['key']
            temp_epic_dict['start'] = epic_dict['start'].strftime("%Y-%m-%d")
            temp_epic_dict['done'] =  epic_dict['done'].strftime("%Y-%m-%d")
            temp_epic_dict['takt'] = takt_list
            takt_data.append(temp_epic_dict)
            #pprint(temp_epic_dict)

    with open(out_file, 'w') as outfile:
        json.dump(processed_data, outfile)

    with open(data_file, 'w') as datafile:
        json.dump(takt_data, datafile)


'''
Input format:
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

 Output format:
[
	[6, 3, 3, 3, 3, 7, 1, 1, 1, 1, 1, 1, 36],
	[0, 1, 1, 2, 2, 2, 2, 2, 4, 7, 7, 1]
]
 '''
