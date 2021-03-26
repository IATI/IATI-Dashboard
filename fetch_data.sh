#!/bin/bash

# Store list of current download errors
mkdir -p data/downloads/
wget "https://gist.githubusercontent.com/codeforIATIbot/f117c9be138aa94c9762d57affc51a64/raw/errors" -O data/downloads/errors

# Get CKAN (IATI Registry) data
rm -rf data/ckan_publishers/
python fetch_data.py

# Generate a csv file with the number of download errors logged since 2013
cd data/downloads
echo "cloning download errors"
if [ ! -d ./f117c9be138aa94c9762d57affc51a64 ]; then
    git clone https://gist.github.com/f117c9be138aa94c9762d57affc51a64.git
fi
cd ./f117c9be138aa94c9762d57affc51a64
echo "cloned download errors - checking out commits"
git checkout master > /dev/null
git pull > /dev/null
for commit in `git log --format=format:%H`; do
    git checkout $commit
    date=`git log -1 --format="%ai"`
    count=`cat errors | grep -v '^\.$' | wc -l`
    echo $date,$count
done > ../history.csv
echo "cloned and checked out download errors"
cd ../../../

# Get codelists for versions v1.x and v2.x of the IATI Standard
cd data
echo "cloning Codelists-1"
if [ ! -d IATI-Codelists-1 ]; then
    git clone https://github.com/IATI/IATI-Codelists.git IATI-Codelists-1
fi
cd IATI-Codelists-1
echo "checking out Codelists-1"
git checkout version-1.05 > /dev/null
git pull > /dev/null
echo "running gen.sh for Codelist-1"
./gen.sh

cd ..
echo "cloning Codelists-2"
if [ ! -d IATI-Codelists-2 ]; then
    git clone https://github.com/andylolz/IATI-Codelists.git IATI-Codelists-2
fi
cd IATI-Codelists-2
echo "checking out Codelists-2"
git checkout version-2.03 > /dev/null
git pull > /dev/null
echo "running gen.sh for Codelist-2"
./gen.sh

echo "completed fetching data"
