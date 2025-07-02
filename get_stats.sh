set -eux
# ^ https://explainshell.com/explain?cmd=set+-eux

mkdir stats-calculated
for f in ckan gitdate licenses; do
    curl --compressed "https://ati.dev.merged.dashboard.iatistandard.org/stats/${f}.json" > stats-calculated/${f}.json
done

cd stats-calculated
wget "https://ati.dev.merged.dashboard.iatistandard.org/stats/current.tar.gz" -O current.tar.gz
wget "https://ati.dev.merged.dashboard.iatistandard.org/stats/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
wget "https://ati.dev.merged.dashboard.iatistandard.org/stats/gitaggregate-publisher-dated.tar.gz" -O gitaggregate-publisher-dated.tar.gz
tar -xf current.tar.gz
tar -xf gitaggregate-dated.tar.gz
tar -xf gitaggregate-publisher-dated.tar.gz
