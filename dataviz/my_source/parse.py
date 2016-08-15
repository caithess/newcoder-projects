'''
Kate Hess
from newcoder.io Data Viz project
(doing this again to refresh)
August 15, 2016
'''

"""
Data Visualization Project
Parse data from an ugly CSV or Excel file, and render it in
JSON, save to a database, and visualize in graph form.

Part I: Taking data from a CSV/Excel file, and return it into a format
that is easier for Python to play with.

Copyright (c) 2013 E. Lynn Root
Distributed under the zlib png license. See LICENSE for details.
"""


import csv
import json
import os

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
    return parsed_data


def main():
    # Boilerplate
    # call our parse function and give it the needed parameters
    new_data = parse(MY_FILE, ',')


if __name__ == "__main__":
    main()
