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

import requests
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

import tablib
from giantbomb_api import api_key

CPI_DATA_URL = 'http://research.stlouisfed.org/fred2/data/CPIAUCSL.txt'


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

    def __str__(self):
        return ("CPI data for" + self.country + "from" + self.first_year +
                "to" + self.last_year)

    def load_from_url(self, url, save_as_file=None):
        '''Loads data from a given url. Option to save externally.
        After getting file this fn uses load_from_file internally.'''
        data = requests.get(url, stream=True,
                            headers={'Accept-Encoding': None}).raw
        # writes to file if needed
        if save_as_file is not None:
            with open(save_as_file, "wb+") as out:
                while True:
                    buffer = data.read(81920)
                    if not buffer:
                        break
                    out.write(buffer)
        return self.load_from_file(data)

    def load_from_file(self, file):
        '''Loads CPI data from given file-like object.'''
        current_year = None
        year_cpi = []
        for line in file:
            # skips pre-data misc infotext
            while not line.startswith("DATE"):
                pass
            # remove end newline; split data text into cols
            data = line.rstrip.split()
            # parse date and CPI
            year = int(data[0].split("-")[0])
            cpi = float(data[1])
            # set up first and last years
            if self.first_year is None or self.first_year > year:
                self.first_year = year
            if self.last_year is None or self.last_year < year:
                self.last_year = year
            # calculate CPI for each year
            if current_year != year:
                if current_year is not None:
                    # enter average of that year's CPIs into master dict
                    self.year_cpi[current_year] = sum(year_cpi) / len(year_cpi)
                # reset everything
                year_cpi = []
                current_year = year
            year_cpi.append(cpi)
        # finally, calculate CPI for last year in data
        if current_year is not None and current_year not in self.year_cpi:
            self.year_cpi[current_year] = sum(year_cpi) / len(year_cpi)

    def get_adjusted_price(self, price, year, current_year=self.last_year):
        '''Returns adjusted price from a given year compared to
        specified current year.'''
        # Use edge data if given year not in CPI dataset
        year = max(self.first_year, year)
        year = min(self.last_year, year)

        year_cpi = self.year_cpi[year]
        current_cpi = self.year_cpi[current_year]
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
        # Set up for getting full result set
        incomplete = True
        num_total = None
        num_returned = 0
        counter = 0
        while incomplete:
            # GiantbombAPI has page limit = 100
            params['offset'] = num_returned
            result = requests.get(self.base_url + '/platforms/', params=params)
            result = result.json()
            if not num_total:
                num_total = int(result.number_of_total_results)
            num_returned += int(result.number_of_page_results)
            if num_returned >= num_total:
                incomplete = False
            for row in result.results:
                msg = "Yielding platform {0} of {1}"
                logging.debug(msg.format(counter + 1, num_total_results))
                if 'original_price' in row and row.original_price:
                    row['original_price'] = float(row.original_price)
                # Implement as a generator
                yield row
                counter += 1


def is_valid_dataset(platform):
    '''Helper function for GiantbombAPI generator. Removes data w/o release
    data and/or original price. Takes in dict w/ keys (name, abbrev).'''
    if 'name' not in platform or not platform.name:
        logging.warn(u"No platform name found for given dataset.")
        return False
    if 'release_date' not in platform or not platform.release_date:
        logging.warn(u"{0} has no release date.".format(platform.name))
        return False
    if 'original_price' not in platform or not platform.original_price:
        logging.warn(u"{0} has no original price.".format(platform.name))
        return False
    if 'abbrev' not in platform or not platform.abbrev:
        logging.warn(u"{0} has no abbreviation.".format(platform.name))
        return False
    return True


def generate_plot(platforms, outfile):
    '''Generates PNG bar chart of platforms.'''
    labels = []
    values = []
    for platform in platforms:
        name = platform.name
        adj_price = platform.adjusted_price
        price = platform.original_price
        # Remove outlier prices > $2000 for ease of Viz
        if price > 2000:
            continue
        # Replace very long names w/ abbreviation
        if len(name) > 15:
            name = platform.abbreviation
        label = u"{0}\n$ {1}\n$ {2}".format(name, price, round(adj_price, 2))
        labels.insert(0, label)
        values.insert(0, adj_price)
    width = 0.3
    ind = np.arange(len(values))
    fig = plt.figure(figsize=(len(labels) * 1.8, 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(ind, values, width, align='center')
    # Granular formatting/icing
    plt.ylabel('Adjusted Price')
    plt.xlabel('Year / Console')
    ax.set_xticks(ind + 0.3)
    ax.set_xtickslabels(labels)
    fig.autofmt_xdate()
    plt.grid(True)
    # Save plot to file and display it
    plt.show(dpi=72)
    plt.save_fig(outfile, dpi=72)
    plt.clf()


def generate_csv(platforms, outfile):
    '''Writes dataset to CSV file. Takes dict list and filepath/file obj.'''
    headers = ['Abbreviations', 'Name', 'Year', 'Price', 'Adjusted Price']
    dataset = tablib.Dataset(headers=headers)
    for row in platforms:
        fields = ['abbreviation', 'name', 'year', 'original_price',
                  'adjusted_price']
        dataset.append([row[field] for field in fields])
    # If outfile is a string, it's a path we need to open first
    if isinstance(outfile, basestring):
        with open(outfile, 'w+') as out:
            out.write(dataset.csv)
    else:
        outfile.write(dataset.csv)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--giantbomb-api-key', required=True,
                        help='API key provided by Giantbomb.com')
    parser.add_argument('--cpi-file',
                        default=os.path.join(os.path.dirname(__file__),
                                             'CPIAUCSL.txt'),
                        help='Path to file containing the CPI data (also acts'
                             ' as target file if the data has to be downloaded'
                             'first).')
    parser.add_argument('--cpi-data-url', default=CPI_DATA_URL,
                        help='URL which should be used as CPI data source')
    parser.add_argument('--debug', default=False, action='store-true',
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
    return opts


def main():
    '''Contains the main logic for the script.'''

    # Grab CPI/Inflation data.

    # Grab API/game platform data.

    # Figure out the current price of each platform.
    # This will require looping through each game platform we received,
    # and calculate the adjusted price based on the CPI data we also
    # received. During this point, we should also validate our data so
    # we do not skew our results.

    # Generate a plot/bar graph for the adjusted price data.

    # Generate a CSV file to save for the adjusted price data.


if __name__ == "__main__":
    main()
