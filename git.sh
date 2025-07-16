#!/bin/bash
set -eux
# ^ https://explainshell.com/explain?cmd=set+-eux

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Starting Dashboard generation"

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Removing 'out' directory and creating a new one"
rm -rf out || true
mkdir out

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Fetching data"
./fetch_data.sh &> fetch_data.log

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running manage.py dashboard_import"
python manage.py dashboard_import

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running make_plots.py"
python -m iati_dashboard.make_plots

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running make_csv.py"
python manage.py make_csv

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running speakers_kit.py"
python -m iati_dashboard.speakers_kit

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Make a backup of the old web directory and make new content live"
rm -rf web.1 || true # web.1 may not exist
mv web web.1 || true # web may not exist
mv out web

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Dashboard generation complete"
