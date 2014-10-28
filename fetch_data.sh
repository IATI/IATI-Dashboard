#!/bin/bash
mkdir -p data/downloads/
wget "https://gist.github.com/Bjwebb/6726204/raw/errors" -O data/downloads/errors

wget "http://data.tickets.iatistandard.org/query?status=accepted&status=assigned&status=new&status=reopened&format=csv&col=id&col=summary&col=status&col=owner&col=component&col=element&col=data_provider_regisrty_id&order=priority" -O data/issues.csv

wget "http://iatistandard.org/codelists/downloads/clv2/mapping.json" -O data/mapping.json
wget "http://iatistandard.org/codelists/downloads/clv2/json/en/OrganisationType.json" -O data/OrganisationType.json
wget "http://iatistandard.org/codelists/downloads/clv2/json/en/Country.json" -O data/Country.json
wget "http://iatistandard.org/codelists/downloads/clv2/json/en/Region.json" -O data/Region.json

rm -r data/github/
python fetch_data.py

cd data/downloads
if [ ! -d ./6726204 ]; then
    git clone https://gist.github.com/6726204.git
fi
cd ./6726204
git checkout master > /dev/null
git pull > /dev/null
for commit in `git log --format=format:%H`; do
    git checkout $commit
    date=`git log -1 --format="%ai"`
    count=`cat errors | grep -v '^\.$' | wc -l`
    echo $date,$count
done > ../history.csv

cd ../../
if [ ! -d IATI-Codelists ]; then
    git clone https://github.com/IATI/IATI-Codelists.git
fi
cd IATI-Codelists
git checkout version-1.05 > /dev/null
git pull > /dev/null
./gen.sh
