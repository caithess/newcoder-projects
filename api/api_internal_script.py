'''
Data Viz from raw web data and public APIs.

Kate Hess / August 16, 2016 (redoing)
From Lynn Root's newcoder.io - APIs project

Uses Giantbomb.com API and Federal Reserve STL data to calculate a rough
video game price / USD inflation analysis.

http://www.giantbomb.com/api/
http://research.stlouisfed.org/fred2/
'''

import argparse
import logging
import os
import sys
import json
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from matplotlib import pyplot as plt
import datetime
from giantbomb_api import api_key

CPI_DATA_URL = 'http://research.stlouisfed.org/fred2/data/CPIAUCSL.txt'
CPI_FILEPATH = os.path.join(os.path.dirname(__file__), 'CPIAUCSL.txt')
PLOT_FILE = 'myplot.png'
CSV_FILE = 'full_data.csv'
LIMIT = None


class CPIData(object):
    '''Abstraction of FRED CPI data. Stores only one value per year.'''

    def __init__(self):
        # each year as k:v pair
        self.year_cpi = {}
        # remember yearspan in dataset in order to handle years beyond
        # that span
        self.last_year = None
        self.first_year = None
        self.country = "US"
        self.current_year = datetime.datetime.now().year

    def __str__(self):
        return ("CPI data for" + self.country + "from" + self.first_year +
                "to" + self.last_year)

    def load_from_url(self, url, save_as_file=None):
        '''Loads data from a given url. Option to save externally.
        After getting file this fn uses load_from_file internally.'''
        data = requests.get(url, stream=True,
                            headers={'Accept-Encoding': None}).raw
        print("Got FRED CPI data.")
        # writes to file if needed
        if save_as_file is not None:
            with open(save_as_file, "wb+") as out:
                while True:
                    buffer = data.read(81920)
                    if not buffer:
                        break
                    out.write(buffer)
            print("Wrote to file:", save_as_file)
        return self.load_from_file(data)

    def load_from_file(self, file):
        '''Loads CPI data from given file-like object.'''
        current_year = None
        year_cpi = {}
        data = []
        dataline = False
        for line in file:
            if dataline:
                data.append(line.rstrip().split())
            if line.startswith("DATE"):
                dataline = True
        data = pd.DataFrame(data)
        data.columns = ['date', 'cpi']
        data['year'] = data.date.apply(lambda x: int(x.split('-')[0]))
        data['cpi'] = data.cpi.astype(float)
        self.first_year = data.year.min()
        self.last_year = data.year.max()
        groups = data.groupby('year')
        self.year_cpi = groups.mean()
        print("Loaded FRED CPI data from file:", file)

    def get_adjusted_price(self, price, year, current_year=None):
        '''Returns adjusted price from a given year compared to
        specified current year.'''
        # Use edge data if given year not in CPI dataset
        if not current_year:
            current_year = self.current_year
        year = max(self.first_year, year)
        year = min(self.last_year, year)
        year_cpi = self.year_cpi.loc[year]['cpi']
        current_cpi = self.year_cpi.loc[current_year]['cpi']
        return float(price) * current_cpi / year_cpi


class GiantbombAPI(object):
    '''Simple implementation of Giantbomb API that only offers the GET
    /platforms/ call as a generator.'''

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://www.giantbomb.com/api"

    def get_platforms(self, sort=None, filter=None, field_list=None):
        '''Generator for platforms matching criteria. If none passed,
        returns **all** platforms.'''
        # Set up params dict for API call
        params = {}
        if sort:
            params['sort'] = sort
        if field_list:
            params['field_list'] = ','.join(field_list)
        if filter:
            parsed_filter = ['{0}:{1}'.format(k, v) for k, v in filter.items()]
            params['filter'] = ','.join(parsed_filter)
        params['api_key'] = self.api_key
        params['format'] = 'json'
        headers = {'user-agent': 'Chess-Api'}
        # Set up for getting full result set
        incomplete = True
        num_total = None
        num_returned = 0
        counter = 0
        while incomplete:
            # GiantbombAPI has page limit = 100
            params['offset'] = num_returned
            resp = requests.get(self.base_url + '/platforms/', params=params,
                                headers=headers)
            result = resp.json()
            if not num_total:
                num_total = int(result['number_of_total_results'])
            num_returned += int(result['number_of_page_results'])
            if num_returned >= num_total:
                incomplete = False
            for row in result['results']:
                msg = "Yielding platform {0} of {1}"
                logging.debug(msg.format(counter + 1, num_total))
                if 'original_price' in row and row['original_price']:
                    row['original_price'] = float(row['original_price'])
                # Implement as a generator
                yield row
                counter += 1
        print("Retrieved platform dataset.")


def is_valid_dataset(platform):
    '''Helper function for GiantbombAPI generator. Removes data w/o release
    data and/or original price. Takes in dict w/ keys (name, abbrev).'''
    if 'name' not in platform or not platform['name']:
        logging.warn(u"No platform name found for given dataset.")
        return False
    if 'release_date' not in platform or not platform['release_date']:
        logging.warn(u"{0} has no release date.".format(platform['name']))
        return False
    if 'original_price' not in platform or not platform['original_price']:
        logging.warn(u"{0} has no original price.".format(platform['name']))
        return False
    if 'abbreviation' not in platform or not platform['abbreviation']:
        logging.warn(u"{0} has no abbreviation.".format(platform['name']))
        return False
    return True


def generate_plot(platforms, outfile):
    '''Generates PNG bar chart of platforms.'''
    labels = []
    values = []
    for platform in platforms:
        name = platform['abbreviation']
        adj_price = platform['adjusted_price']
        price = platform['original_price']
        # Remove outlier prices > $2000 for ease of Viz
        if price > 2000:
            continue
        label = u"{0} ${1}".format(name, price, round(adj_price, 2))
        labels.insert(0, label)
        values.insert(0, adj_price)
    width = 0.3
    ind = np.arange(len(values))
    fig = plt.figure(figsize=(len(labels), 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(ind, values, width, align='center')
    # Granular formatting/icing
    plt.ylabel('Adjusted Price')
    plt.xlabel('Year / Console')
    ax.set_xticks(ind + 0.3)
    ax.set_xticklabels(labels)
    fig.autofmt_xdate()
    plt.grid(True)
    # Save plot to file and display it
    plt.savefig(outfile)
    plt.clf()
    print("Generated bar plot at file:", outfile)


def generate_csv(platforms, outpath):
    '''Writes dataset to CSV file. Takes dict list and filepath/file obj.'''
    headers = ['Abbreviations', 'Name', 'Year', 'Price', 'Adjusted Price']
    dataset = pd.DataFrame(platforms)
    dataset.to_csv(outpath)
    print("Generated csv of full dataset at file:", outpath)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--giantbomb-api-key',
                        default=api_key,
                        help='API key provided by Giantbomb.com')
    parser.add_argument('--cpi-file',
                        default=os.path.join(os.path.dirname(__file__),
                                             'CPIAUCSL.txt'),
                        help='Path to file containing the CPI data (also acts'
                             ' as target file if the data has to be downloaded'
                             'first).')
    parser.add_argument('--cpi-data-url', default=CPI_DATA_URL,
                        help='URL which should be used as CPI data source')
    parser.add_argument('--debug', default=False, action='store_true',
                        help='Increases the output level')
    parser.add_argument('--csv-file', help='Path to CSV file containing'
                        'data output')
    parser.add_argument('--plot-file', help='Path to PNG file containing'
                        'data bar chart output')
    parser.add_argument('--limit', type=int,
                        help='Number of recent platforms to be considered')
    opts = parser.parse_args()
    if not (opts.plot_file or opts.csv_file):
        parser.error('You have specify either a --csv-file or --plot-file.')
    print("Input arguments parsed.")
    return opts


def main():
    '''Contains the main logic for the script.'''
    # Grab CPI/Inflation data.
    cpi_data = CPIData()
    # Grab API/game platform data.
    gb_api = GiantbombAPI(api_key)

    disclaimer = '''
    Disclaimer: This script uses data provided by FRED (Federal
    Reserve Economic Data) from the Federal Reserve Bank of St. Louis and
    Giantbomb.com:\n- {0}\n- http://www.giantbomb.com/api/\n'''.format(
        CPI_DATA_URL)

    print(disclaimer)

    if os.path.exists(CPI_FILEPATH):
        print("Pulling CPI data from file")
        with open(CPI_FILEPATH) as fp:
            cpi_data.load_from_file(fp)

    else:
        print("Downloading CPI data.")
        cpi_data.load_from_url(CPI_DATA_URL, save_as_file=CPI_FILEPATH)

    # Figure out the current price of each platform.
    # This will require looping through each game platform we received,
    # and calculate the adjusted price based on the CPI data we also
    # received. During this point, we should also validate our data so
    # we do not skew our results.
    platforms = []
    counter = 0

    # Now that we have both data sources set up, fetch the platforms and
    # calculate their current price via the CPI value ratio.
    for platform in gb_api.get_platforms(sort='release_date:desc',
                                         field_list=['release_date',
                                                     'original_price',
                                                     'name',
                                                     'abbreviation']):
        # Skip platforms without release date and/or price
        if not is_valid_dataset(platform):
            continue
        year = int(platform['release_date'].split('-')[0])
        price = platform['original_price']
        adjusted_price = cpi_data.get_adjusted_price(price, year)
        platform['year'] = year
        platform['original_price'] = price
        platform['adjusted_price'] = adjusted_price
        platforms.append(platform)
        # Limit resultset here since we can't on the API level
        if LIMIT is not None and counter + 1 >= LIMIT:
            break
        counter += 1
    print("Generated data for all", counter, "platform observations.")
    df = pd.DataFrame(platforms)
    # Generate a plot/bar graph for the adjusted price data.
    if PLOT_FILE:
        generate_plot(platforms, PLOT_FILE)
    # Generate a CSV file to save for the adjusted price data.
    if CSV_FILE:
        generate_csv(platforms, CSV_FILE)

if __name__ == "__main__":
    main()
