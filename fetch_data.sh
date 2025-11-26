#!/bin/bash
set -eux
# ^ https://explainshell.com/explain?cmd=set+-eux

# Store list of current download errors
mkdir -p data/downloads/
wget "https://gist.githubusercontent.com/codeforIATIbot/f117c9be138aa94c9762d57affc51a64/raw/errors" -O data/downloads/errors

# Get codelists for versions v1.x and v2.x of the IATI Standard
rm -rf data/IATI-Codelists-1
echo "cloning Codelists-1"
git clone --branch version-1.05 https://github.com/IATI/IATI-Codelists.git data/IATI-Codelists-1
cd data/IATI-Codelists-1
echo "running gen.sh for Codelist-1"
./gen.sh
cd ../..

echo "Fetching Codelists-2"
rm -rf data/IATI-Codelists-2
python fetch_v2_codelists.py

echo "Fetching schemas"
rm -rf data/schemas
mkdir data/schemas
cd data/schemas
# for v in 1.01 1.02 1.03 1.04 1.05 2.01 2.02 2.03; do
for v in 1.05 2.03; do
    git clone https://github.com/IATI/IATI-Schemas.git $v
    cd $v
    git checkout version-$v
    git pull
    cd ..
done
cd ..

echo "completed fetching data"
