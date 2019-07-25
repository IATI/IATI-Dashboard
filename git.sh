#!/bin/bash

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Starting Dashboard generation"

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Removing 'out' directory and creating a new one"
rm -rf out
mkdir out

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Fetching data"
./fetch_data.sh &> fetch_data.log || exit 1

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running make_csv.py"
python make_csv.py || exit 1

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running make_html.py"
python make_html.py $1 $2 || exit 1

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Copying static elements"
cp static/img/favicon.png out/
cp static/img/tablesorter-icons.gif out/

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Make a backup of the old web directory and make new content live"
rsync -a --delete web web.bk
mv web web.1
mv out web
rm -rf web.1

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Dashboard generation complete"
