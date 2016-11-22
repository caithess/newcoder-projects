'''
Kate Hess
from newcoder.io Data Viz project
(doing this again to refresh)

Data Visualization Project
Parse data from an ugly CSV or Excel file, and render it in
JSON, save to a database, and visualize in graph form.
August 15, 2016
'''

import csv
import json
import os
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

import geojson

MY_FILE = '../data/sample_sfpd_incident_all.csv'


def parse(raw_file, delimiter):
    '''Parses a raw data CSV file to a JSON-like object.'''

    # Open CSV file
    opened_file = open(raw_file)
    # Read CSV file
    csv_data = csv.reader(opened_file, delimiter=delimiter)
    # Build a data structure to return parsed_data
    parsed_data = []
    # store header row, skips to next line
    fields = next(csv_data)
    # loop over each csv row
    for row in csv_data:
        parsed_data.append(dict(zip(fields, row)))
    # Close CSV file
    opened_file.close()
    # save parsed_data as JSON file
    json_output = {"incidents": parsed_data}
    json_filepath = '../viz_outputs/sample_sfpd_incident_all.json'
    # remove old JSON output file if it exists
    try:
        os.remove(json_filepath)
    except OSError:
        pass
    # write to JSON file
    with open(json_filepath, 'w') as json_outfile:
        json.dump(json_output, json_outfile)

    print("Parsed data to JSON-like object.")
    print("Wrote to JSON file.")
    return parsed_data


def visualize_days(parsed_data):
    '''Takes JSON-like object of parsed data.
    Visualize data by day of week.'''

    # make a new variable 'counter' from iterating through each line of
    # data in the parsed data, and count how many incidents happen on
    # each day of each week
    counter = Counter(item['DayOfWeek'] for item in parsed_data)
    # separate the x-axis data (the days of the week) from the 'counter'
    # variable from the y-axis data (the number of incidents each day)
    data_list = [
        counter['Monday'],
        counter['Tuesday'],
        counter['Wednesday'],
        counter['Thursday'],
        counter['Friday'],
        counter['Saturday'],
        counter['Sunday']
    ]
    # create x-axis string labels
    day_tuple = tuple(["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"])
    # with that y-axis data, assign it to a matplotlib instance
    plt.plot(data_list)
    # create the amount of ticks needed for x-axis and assign labels
    plt.xticks(range(len(day_tuple)), day_tuple)
    # create save filepath
    outpath = "../viz_outputs/Days.png"
    # remove old output file if it exists
    try:
        os.remove(outpath)
    except OSError:
        pass
    # save the plot
    plt.savefig(outpath)
    # close plot file
    plt.clf()
    print("Saved Days graph.")


def visualize_type(parsed_data):
    """Visualize data from JSON-like obj by category in a bar graph"""

    # make a new variable, 'counter', from iterating through each line
    # of data in the parsed data, and count how many incidents happen
    # by category
    counter = Counter(item['Category'] for item in parsed_data)
    # Set the labels which are based on the keys of our counter.
    # Since order doesn't matter, we can just used counter.keys()
    labels = tuple(counter.keys())
    # Set exactly where the labels hit the x-axis
    xlocations = np.arange(len(labels)) + 0.5
    # Width of each bar that will be plotted
    width = 0.5
    # Assign data to a bar plot (similar to plt.plot()!)
    plt.bar(xlocations, counter.values(), width=width)
    # Assign labels and tick location to x-axis
    plt.xticks(xlocations + width / 2, labels, rotation=90)
    # Give some more room so the x-axis labels aren't cut off in the
    # graph
    plt.subplots_adjust(bottom=0.4)
    # Make the overall graph/figure is larger
    plt.rcParams['figure.figsize'] = 12, 8
    # create save filepath
    outpath = "../viz_outputs/Type.png"
    # remove old output file if it exists
    try:
        os.remove(outpath)
    except OSError:
        pass
    # save the plot
    plt.savefig(outpath)
    # close plot file
    plt.clf()
    print("Saved Types graph.")


def create_map(parsed_data):
    '''Takes JSON-like data file to GeoJSON file.'''
    # Define type of GeoJSON we're creating
    geo_map = {"type": "FeatureCollection"}
    # Define empty list to collect each point to graph
    item_list = []
    # Iterate over our data to create GeoJSON document.
    # We're using enumerate() so we get the line, as well
    # the index, which is the line number.
    for index, row in enumerate(parsed_data):
        # Skip any zero coordinates as this will throw off
        # our map.
        if float(row['X']) == 0 or float(row['Y']) == 0:
            continue
        # Setup a new dictionary for each iteration.
        data = {}
        # Assign line items to appropriate GeoJSON fields.
        data['type'] = 'Feature'
        data['id'] = index
        data['properties'] = {'title': row['Category'],
                              'description': row['Descript'],
                              'date': row['Date']}
        data['geometry'] = {'type': 'Point',
                            'coordinates': (row['X'], row['Y'])}
        # Add data dictionary to our item_list
        item_list.append(data)

    # For each point in our item_list, we add the point to our
    # dictionary.  setdefault creates a key called 'features' that
    # has a value type of an empty list.  With each iteration, we
    # are appending our point to that list.
    for point in item_list:
        geo_map.setdefault('features', []).append(point)
    # Now that all data is parsed in GeoJSON write to a file so we
    # can upload it to gist.github.com
    # remove old output if it exists
    outpath = '../viz_outputs/file_sf.geojson'
    try:
        os.remove(outpath)
    except OSError:
        pass
    # save file
    with open(outpath, 'w') as f:
        f.write(geojson.dumps(geo_map))
    print("Saved to GeoJSON file.")
    return geo_map


def main():
    # Boilerplate
    parsed_data = parse(MY_FILE, ',')
    visualize_days(parsed_data)
    visualize_type(parsed_data)
    return create_map(parsed_data)

if __name__ == "__main__":
    main()
