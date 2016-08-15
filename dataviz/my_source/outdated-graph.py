'''
Kate Hess
August 16, 2016
from newcoder.io - Data Viz Project
'''
"""
Data Visualization Project
Parse data from an ugly CSV or Excel file, and render it in
JSON-like form, visualize in graphs, and plot on Google Maps.

Part II: Take the data we just parsed and visualize it using popular
Python math libraries.
"""

from collections import Counter

import csv
import os
import matplotlib.pyplot as plt
import numpy as np

from parse import parse, MY_FILE

def visualize_days():
    '''Takes JSON-like object of parsed data.
    Visualize data by day of week.'''

    # Grab our parsed data we parsed earlier in parse.py
    data_file = parse(MY_FILE, ',')
    # make a new variable 'counter' from iterating through each line of
    # data in the parsed data, and count how many incidents happen on
    # each day of each week
    counter = Counter(item['DayOfWeek'] for item in data_file)
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


def visualize_type():
    """Visualize data from JSON-like obj by category in a bar graph"""

    # grab our parsed data
    data_file = parse(MY_FILE, ',')
    # make a new variable, 'counter', from iterating through each line
    # of data in the parsed data, and count how many incidents happen
    # by category
    counter = Counter(item['Category'] for item in data_file)
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


def main():
    visualize_days()
    visualize_type()

if __name__ == "__main__":
    main()
