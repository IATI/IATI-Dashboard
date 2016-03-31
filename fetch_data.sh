#!/bin/bash
mkdir -p data/downloads/
wget "https://gist.github.com/iati-bot/4f86dc7b36562c8b2b21/raw/errors" -O data/downloads/errors

wget "http://data.tickets.iatistandard.org/query?status=accepted&status=assigned&status=new&status=reopened&format=csv&col=id&col=summary&col=status&col=owner&col=component&col=element&col=data_provider_regisrty_id&order=priority" -O data/issues.csv

rm -r data/github/
python fetch_data.py

cd data/downloads
if [ ! -d ./4f86dc7b36562c8b2b21 ]; then
    git clone https://gist.github.com/4f86dc7b36562c8b2b21.git
fi
cd ./4f86dc7b36562c8b2b21
git checkout master > /dev/null
git pull > /dev/null
for commit in `git log --format=format:%H`; do
    git checkout $commit
    date=`git log -1 --format="%ai"`
    count=`cat errors | grep -v '^\.$' | wc -l`
    echo $date,$count
done > ../history.csv

cd ../../
if [ ! -d IATI-Codelists-1 ]; then
    git clone https://github.com/IATI/IATI-Codelists.git IATI-Codelists-1
fi
cd IATI-Codelists-1
git checkout version-1.05 > /dev/null
git pull > /dev/null
./gen.sh

cd ..
if [ ! -d IATI-Codelists-2 ]; then
    git clone https://github.com/IATI/IATI-Codelists.git IATI-Codelists-2
fi
cd IATI-Codelists-2
git checkout version-2.02 > /dev/null
git pull > /dev/null
./gen.sh
