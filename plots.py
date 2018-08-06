#!/usr/bin/env python
"""
Show how to make date plots in matplotlib using date tick locators and
formatters.  See major_minor_demo1.py for more information on
controlling major and minor ticks

All matplotlib date plotting is done by converting date instances into
days since the 0001-01-01 UTC.  The conversion, tick locating and
formatting is done behind the scenes so this is most transparent to
you.  The dates module provides several converter functions date2num
and num2date

"""
from __future__ import print_function
import datetime
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

import os
import unicodecsv
import common
import data

#  Import failed_downloads as a global
failed_downloads = unicodecsv.reader(open('data/downloads/history.csv'))

gitaggregate_publisher = data.JSONDir('./stats-calculated/gitaggregate-publisher-dated')

class AugmentedJSONDir(data.JSONDir):
    def __getitem__(self, key):
        if key == 'failed_downloads':
            return dict((row[0],row[1]) for row in failed_downloads)
        elif key == 'publisher_types':
            out = defaultdict(lambda: defaultdict(int))
            for publisher, publisher_data in gitaggregate_publisher.iteritems():
                if publisher in data.ckan_publishers:
                    organization_type = common.get_publisher_type(publisher)['name']
                    for datestring,count in publisher_data['activities'].iteritems():
                        out[datestring][organization_type] += 1
                else:
                    print('Publisher not matched:', publisher)
            return out
        elif key == 'activities_per_publisher_type':
            out = defaultdict(lambda: defaultdict(int))
            for publisher, publisher_data in gitaggregate_publisher.iteritems():
                if publisher in data.ckan_publishers:
                    organization_type = common.get_publisher_type(publisher)['name']
                    for datestring,count in publisher_data['activities'].iteritems():
                        out[datestring][organization_type] += count
                else:
                    print('Publisher not matched:', publisher)
            return out
        else: 
            return super(AugmentedJSONDir, self).__getitem__(key)


from vars import expected_versions

def make_plot(stat_path, git_stats, img_prefix=''):
    if type(stat_path) == tuple:
        stat_name = stat_path[0]
    else:
        stat_name = stat_path
    
    print('-> ', stat_name)
   
    stat_dict = git_stats.get(stat_name)
    if not stat_dict:
        return
    items = sorted(stat_dict.items())
    x_values = [ datetime.date(int(x[0:4]), int(x[5:7]), int(x[8:10])).toordinal() for x,y in items ]
    if type(stat_path) == tuple:
        y_values = [ dict((k,v) for k,v in y.iteritems() if stat_path[1](k)) for x,y in items ]
    else:
        y_values = [ y for x,y in items ]

    #years    = mdates.YearLocator()   # every year
    #months   = mdates.MonthLocator()  # every month
    dateFmt = mdates.DateFormatter('%Y-%m-%d')

    fig, ax = plt.subplots()
    ax.set_color_cycle(['b', 'g', 'r', 'c', 'm', 'y', 'k', '#00ff00', '#fc5ab8', '#af31f2'])
    fig_legend = plt.figure()
    dpi = 96
    fig.set_size_inches(600.0/dpi, 600.0/dpi)
    if type(y_values[0]) == dict:
        keys = set([ tm for y in y_values for tm in y.keys() ])
        plots = {}
        for key in keys:
            plots[key], = ax.plot(x_values, [ y.get(key) or 0 for y in y_values ])
        if stat_name in ['publisher_types', 'activities_per_publisher_type']:
            # Sort by the most recent value for the key
            sorted_items = sorted(plots.items(), key=lambda x: y_values[-1][x[0]], reverse=True)
            fig_legend.legend([x[1] for x in sorted_items], [x[0] for x in sorted_items], 'center', ncol=1)
            fig_legend.set_size_inches(600.0/dpi, 300.0/dpi)
        else:
            fig_legend.legend(plots.values(), plots.keys(), 'center', ncol=4)
            fig_legend.set_size_inches(600.0/dpi, 100.0/dpi)
        fig_legend.savefig('out/{0}{1}{2}_legend.png'.format(img_prefix,stat_name,stat_path[2]))
    else:
        keys = None
        ax.plot(x_values, y_values)


    # format the ticks
    #ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(dateFmt)
    #ax.xaxis.set_minor_locator(months)

    #datemin = datetime.date(r.date.min().year, 1, 1)
    #datemax = datetime.date(r.date.max().year+1, 1, 1)
    #ax.set_xlim(datemin, datemax)

    # format the coords message box
    #def price(x): return '$%1.2f'%x
    #ax.format_ydata = price
    ax.xaxis_date()
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    fig.savefig('out/{0}{1}{2}.png'.format(img_prefix,stat_name,stat_path[2] if type(stat_path) == tuple else ''), dpi=dpi)
    plt.close('all')

    fn = 'out/{0}{1}.csv'.format(img_prefix,stat_name)
    with open(fn, 'w') as fp:
        writer = unicodecsv.writer(fp)
        if keys:
            sorted_keys = sorted(list(keys))
            writer.writerow(['date'] + sorted_keys)
        else:
            writer.writerow(['date', 'value'])
        for k,v in items:
            if keys:
                writer.writerow([k] + [ v.get(key) for key in sorted_keys ])
            else:
                writer.writerow([k,v])
        del writer


# Load aggregated stats for all data
print("All data")
git_stats = AugmentedJSONDir('./stats-calculated/gitaggregate-dated')

for stat_path in [
        'activities',
        'publishers',
        'activity_files',
        'organisation_files',
        'file_size',
        'failed_downloads',
        'invalidxml',
        'nonstandardroots',
        'unique_identifiers',
        ('validation', lambda x: x=='fail', ''),
        ('publishers_validation', lambda x: x=='fail', ''),
        ('publisher_has_org_file', lambda x: x=='no', ''),
        ('versions', lambda x: x in expected_versions, '_expected'),
        ('versions', lambda x: x not in expected_versions, '_other'),
        ('publishers_per_version', lambda x: x in expected_versions, '_expected'),
        ('publishers_per_version', lambda x: x not in expected_versions, '_other'),
        ('file_size_bins', lambda x: True, ''),
        ('publisher_types', lambda x: True, '' ),
        ('activities_per_publisher_type', lambda x: True, '' )
        ]:
#    pdb.set_trace()
    make_plot(stat_path, git_stats)

# Delete git_stats variable to save memory
del git_stats

try:
    os.makedirs('out/publisher_imgs')
except OSError:
    pass

git_stats_publishers = AugmentedJSONDir('./stats-calculated/gitaggregate-publisher-dated/')
for publisher, git_stats_publisher in git_stats_publishers.iteritems():
    print(publisher)
    for stat_path in [
            'activities',
            'activity_files',
            'organisation_files',
            'file_size',
            'invalidxml',
            'nonstandardroots',
            'publisher_unique_identifiers',
            ('validation', lambda x: x=='fail', ''),
            ('versions', lambda x: True, ''),
            ]:
        make_plot(stat_path, git_stats_publisher, 'publisher_imgs/{0}_'.format(publisher))

