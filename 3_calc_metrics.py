# -*- coding: utf-8 -*-
#from bokeh.charts import Bar, output_file, show
from datetime import datetime
import json
import numpy as np
import pandas as pd
from pprint import pprint

in_file = "takt_times.json"
out_file = "metrics.json"


### MAIN ###
if __name__ == '__main__':
    #GET THE FEATURE DATA
    try:
        with open(in_file, 'r') as infile:
            processed_data = json.load(infile)
    except Exception as e:
        print e
        exit()

    ##################################################
    # Only use data within the timeframe of interest
    ##################################################

    takt_distro = {}
    issue_list = []
    duration_list = []
    average_takt_list = []

    for epic in processed_data:
        ##################################################
        # Get the duration of the epic
        ##################################################
        duration_list.append(sum(epic))
        average_takt_list.append(float(sum(epic))/float(len(epic)))

        ##################################################
        # Update the distro of "takt" times
        ##################################################
        for entry in epic:
            issue_list.append(entry)
            if entry in takt_distro.keys():
                takt_distro[entry] = takt_distro[entry] + 1
            else:
                takt_distro[entry] = 1

    ##################################################
    # Prep the data for the probhability distribution
    ##################################################
    #TODO MOVE TO PROCESS_DATA
    #
    bins = []
    takt  = []
    data = {}

    current = 0
    total = 0
    for key, value in takt_distro.iteritems():
        while current <= key:
            if current == int(key):
                bins.append(key)
                takt.append(value)
                total = total + value
            else:
                bins.append(current)
                takt.append(0)
            current = current + 1

    data = {
        'days': bins,
        'time': takt,
        'p(t)': []
        }

    # Create the probability Ditribution Manually
    # TODO do this through Pandas, Numpy, SciPy later
    for day in takt:
        prob = float(day) / float(total)
        data['p(t)'].append(prob)

    # Write to file
    with open(out_file, 'w') as outfile:
        json.dump(data, outfile)

    today = datetime.now()
    out_file = today + '_' + outfile

    with open(out_file, 'w') as outfile:
        json.dump(data, outfile)

    ##################################################
    # Plot the histogram
    ##################################################
    '''
    df = pd.DataFrame(data)
    hist = Bar(df, 'days', values='time', title="test chart")

    output_file("project_done.html")
    show(hist)
    '''

    ##################################################
    # Epic Macro Metrics
    ##################################################
    metric_dict = {}

    #Average (days/item)
    metric_dict['epic_avg'] = np.average(duration_list)
    metric_dict['takt_avg'] = np.average(issue_list)
    metric_dict['takt_avg2'] = np.average(average_takt_list)

    # Median
    metric_dict['epic_median'] = np.median(duration_list)
    metric_dict['takt_median'] = np.median(issue_list)

    # Std Deviation
    metric_dict['epic_stddev'] = np.std(duration_list)
    metric_dict['takt_stddev'] = np.std(issue_list)

    pprint(metric_dict)

    # Write to file - timestamp
    metric_dict_file = '%s-%s-%s_metric_dict.json' % (today.year, today.month, today.day)
    with open(metric_dict_file, 'w') as outfile:
        json.dump(data, outfile)

    #print issue_list
    #pprint(takt_distro)


    ##################################################
    # TODO Rolling Average (days)
    # NEED TO SORT PROCESSED_DATA BY DELIVERY DATE
    ##################################################
    #pprint(sort_done(processed_data))
    #print moving_average(processed_data)


    ##################################################
    # TODO Running average of # Features in Progress
    ##################################################

'''
Input format:
[
	[6, 3, 3, 3, 3, 7, 1, 1, 1, 1, 1, 1, 36],
	[0, 1, 1, 2, 2, 2, 2, 2, 4, 7, 7, 1]
]

Output format:
{
	"p(t)": [0.12396694214876033, 0.256198347107438, 0.1115702479338843, ...0.008264462809917356],
	"days": [0, 1, 2, ...131],
	"time": [30, 62, 27, ...2]
}
 '''
