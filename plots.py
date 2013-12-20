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
import datetime
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import json, re
git_stats = json.load(open('./stats-calculated/gitaggregate-dated.json'))

from vars import expected_versions

for stat_path in [
        'activities',
        'publishers',
        'activity_files',
        'spend',
        'file_size',
        ('validation', lambda x: x=='fail', ''),
        ('publishers_validation', lambda x: x=='fail', ''),
        ('publisher_has_org_file', lambda x: x=='no', ''),
        ('versions', lambda x: x in expected_versions, '_expected'),
        ('versions', lambda x: x not in expected_versions, '_other'),
        ('publishers_per_version', lambda x: x in expected_versions, '_expected'),
        ('publishers_per_version', lambda x: x not in expected_versions, '_other')
        ]:
    if type(stat_path) == tuple:
        stat_name = stat_path[0]
    else:
        stat_name = stat_path
    
    items = sorted(git_stats.get(stat_name).items())
    x_values = [ datetime.date(int(x[0:4]), int(x[5:7]), int(x[8:10])).toordinal() for x,y in items ]
    if type(stat_path) == tuple:
        y_values = [ dict((k,v) for k,v in y.items() if stat_path[1](k)) for x,y in items ]
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
        fig_legend.legend(plots.values(), plots.keys(), 'center', ncol=4)
        fig_legend.set_size_inches(600.0/dpi, 100.0/dpi)
        fig_legend.savefig('out/{0}{1}_legend.png'.format(stat_name,stat_path[2]))
    else:
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
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    #ax.format_ydata = price
    ax.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    fig.savefig('out/{0}{1}.png'.format(stat_name,stat_path[2] if type(stat_path) == tuple else ''), dpi=dpi)
    plt.close()

