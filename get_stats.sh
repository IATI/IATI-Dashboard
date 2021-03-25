# This script is the same as https://github.com/IATI/IATI-Stats/blob/master/get_stats.sh
# but with only the dated historical aggregates.
mkdir stats-calculated
for f in ckan gitdate; do
    curl --compressed "http://dashboard.iatistandard.org/stats/${f}.json" > stats-calculated/${f}.json
done

mkdir stats-blacklist
cd stats-blacklist
wget "http://dashboard.iatistandard.org/stats-blacklist/current.tar.gz" -O current.tar.gz
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
wget "http://dashboard.iatistandard.org/stats-blacklist/gitaggregate-publisher-dated.tar.gz" -O gitaggregate-publisher-dated.tar.gz
tar -xf current.tar.gz
tar -xf gitaggregate-dated.tar.gz
tar -xf gitaggregate-publisher-dated.tar.gz
cd ..

cd stats-calculated
wget "http://dashboard.iatistandard.org/stats/current.tar.gz" -O current.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-publisher-dated.tar.gz" -O gitaggregate-publisher-dated.tar.gz
tar -xf current.tar.gz
tar -xf gitaggregate-dated.tar.gz
tar -xf gitaggregate-publisher-dated.tar.gz
