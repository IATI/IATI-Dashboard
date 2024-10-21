#!/usr/bin/env python
""" Generates static images of stats graphs using matplotlib.
"""

import logging
import datetime
import argparse
import os  # noqa: F401
from collections import defaultdict
import csv

import numpy as np  # noqa: F401
from tqdm import tqdm
import common
import data
import config
from vars import expected_versions  # noqa: F401
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.dates as mdates  # noqa: E402


logger = logging.getLogger(__name__)


class AugmentedJSONDir(data.JSONDir):
    def __init__(self, folder, failed_downloads, gitaggregate_publisher):
        super().__init__(folder)
        self.failed_downloads = failed_downloads
        self.gitaggregate_publisher = gitaggregate_publisher

    def __getitem__(self, key):
        if key == 'failed_downloads':
            return dict((row[0], row[1]) for row in self.failed_downloads)
        elif key == 'publisher_types':
            out = defaultdict(lambda: defaultdict(int))
            for publisher, publisher_data in self.gitaggregate_publisher.items():
                if publisher in data.ckan_publishers:
                    organization_type = common.get_publisher_type(publisher)['name']
                    for datestring, count in publisher_data['activities'].items():
                        out[datestring][organization_type] += 1
                else:
                    logger.debug("Getting by publisher_type unmatched publisher <{}>".format(publisher))
            return out
        elif key == 'activities_per_publisher_type':
            out = defaultdict(lambda: defaultdict(int))
            for publisher, publisher_data in self.gitaggregate_publisher.items():
                if publisher in data.ckan_publishers:
                    organization_type = common.get_publisher_type(publisher)['name']
                    for datestring, count in publisher_data['activities'].items():
                        out[datestring][organization_type] += count
                else:
                    logger.debug("Getting by activities_per_publisher_type unmatched publisher <{}>".format(publisher))
            return out
        else:
            return super(AugmentedJSONDir, self).__getitem__(key)


def make_plot(stat_path, git_stats, img_prefix=''):
    if type(stat_path) is tuple:
        stat_name = stat_path[0]
    else:
        stat_name = stat_path

    stat_dict = git_stats.get(stat_name)
    if not stat_dict:
        return
    items = sorted(stat_dict.items())
    x_values = [datetime.date(int(x[0:4]), int(x[5:7]), int(x[8:10])) for x, y in items]
    if type(stat_path) is tuple:
        y_values = [dict((k, v) for k, v in y.items() if stat_path[1](k)) for x, y in items]
    else:
        y_values = [float(y) for x, y in items]

    # years    = mdates.YearLocator()   # every year
    # months   = mdates.MonthLocator()  # every month
    datefmt = mdates.DateFormatter('%Y-%m-%d')

    fig, ax = plt.subplots()
    ax.set_prop_cycle('color', ['b', 'g', 'r', 'c', 'm', 'y', 'k', '#00ff00', '#fc5ab8', '#af31f2'])
    fig_legend = plt.figure()
    dpi = 96
    fig.set_size_inches(600.0 / dpi, 600.0 / dpi)

    if type(y_values[0]) is dict:
        keys = set([tm for y in y_values for tm in y.keys()])
        plots = {}
        for key in keys:
            plots[key], = ax.plot(x_values, [y.get(key) or 0 for y in y_values])
        if stat_name in ['publisher_types', 'activities_per_publisher_type']:
            # Sort by the most recent value for the key
            sorted_items = sorted(plots.items(), key=lambda x: y_values[-1][x[0]], reverse=True)
            fig_legend.legend([x[1] for x in sorted_items], [x[0] for x in sorted_items], loc='center', ncol=1)
            fig_legend.set_size_inches(600.0 / dpi, 300.0 / dpi)
        else:
            fig_legend.legend(plots.values(), plots.keys(), loc='center', ncol=4)
            fig_legend.set_size_inches(600.0 / dpi, 100.0 / dpi)
        fig_legend.savefig(config.join_out_path('{0}{1}{2}_legend.png'.format(img_prefix, stat_name, stat_path[2])))
    else:
        keys = None
        ax.plot(x_values, y_values)

    # format the ticks
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(datefmt)
    # ax.xaxis.set_minor_locator(months)

    # datemin = datetime.date(r.date.min().year, 1, 1)
    # datemax = datetime.date(r.date.max().year+1, 1, 1)
    # ax.set_xlim(datemin, datemax)

    # format the coords message box
    # def price(x): return '$%1.2f'%x
    # ax.format_ydata = price
    ax.xaxis_date()
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    ax.ticklabel_format(axis='y', style='plain', useOffset=False)

    fig.savefig(config.join_out_path('{0}{1}{2}.png'.format(img_prefix, stat_name, stat_path[2] if type(stat_path) is tuple else '')), dpi=dpi)
    plt.close('all')

    fn = config.join_out_path('{0}{1}.csv'.format(img_prefix, stat_name))
    with open(fn, 'w') as fp:
        writer = csv.writer(fp)
        if keys:
            sorted_keys = sorted(list(keys))
            writer.writerow(['date'] + sorted_keys)
        else:
            writer.writerow(['date', 'value'])
        for k, v in items:
            if keys:
                writer.writerow([k] + [v.get(key) for key in sorted_keys])
            else:
                writer.writerow([k, v])
        del writer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Generate images verbosely to stdout")
    args = parser.parse_args()

    # Load data required for loading stats.
    failed_downloads = csv.reader(open(config.join_data_path('downloads/history.csv')))
    gitaggregate_publisher = data.JSONDir(config.join_stats_path('gitaggregate-publisher-dated'))

    # Generate plots for aggregated stats for all data.
    logger.info("Generating plots for all aggregated data")
    git_stats = AugmentedJSONDir(config.join_stats_path('gitaggregate-dated'),
                                 failed_downloads,
                                 gitaggregate_publisher)
    os.makedirs(config.join_out_path('img/aggregate'), exist_ok=True)

    _paths = [
            'activities',
            'publishers',
            'activity_files',
            'organisation_files',
            'file_size',
            'failed_downloads',
            'invalidxml',
            'nonstandardroots',
            'unique_identifiers',
            ('validation', lambda x: x == 'fail', ''),
            ('publishers_validation', lambda x: x == 'fail', ''),
            ('publisher_has_org_file', lambda x: x == 'no', ''),
            ('versions', lambda x: x in expected_versions, '_expected'),
            ('versions', lambda x: x not in expected_versions, '_other'),
            ('publishers_per_version', lambda x: x in expected_versions, '_expected'),
            ('publishers_per_version', lambda x: x not in expected_versions, '_other'),
            ('file_size_bins', lambda x: True, ''),
            ('publisher_types', lambda x: True, ''),
            ('activities_per_publisher_type', lambda x: True, '')
    ]
    with tqdm(total=len(_paths)) as pbar:
        if args.verbose:
            pbar.set_description("Generate aggregate plots")
        for stat_path in _paths:
            if args.verbose:
                pbar.update()
            make_plot(stat_path, git_stats, img_prefix='img/aggregate/')

    # Delete git_stats variable to save memory
    del git_stats

    # Generate plots for each publisher.
    logger.info("Generating plots for all publishers")
    git_stats_publishers = AugmentedJSONDir(config.join_stats_path('gitaggregate-publisher-dated/'),
                                            failed_downloads,
                                            gitaggregate_publisher)
    os.makedirs(config.join_out_path('img/publishers'), exist_ok=True)

    with tqdm(total=len(git_stats_publishers)) as pbar:
        if args.verbose:
            pbar.set_description("Generate plots for all publishers")
        for publisher, git_stats_publisher in git_stats_publishers.items():
            if args.verbose:
                pbar.update()
            for stat_path in [
                    'activities',
                    'activity_files',
                    'organisation_files',
                    'file_size',
                    'invalidxml',
                    'nonstandardroots',
                    'publisher_unique_identifiers',
                    ('validation', lambda x: x == 'fail', ''),
                    ('versions', lambda x: True, ''),
            ]:
                make_plot(stat_path, git_stats_publisher, img_prefix='img/publishers/{0}_'.format(publisher))


if __name__ == "__main__":
    main()
