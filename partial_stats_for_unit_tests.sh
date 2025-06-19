set -eux

publisher_short_name=zsl

if [ -d stats-calculated ]; then
    echo "stats-calculated directory already exists, exiting."
    exit
fi
wget -m --no-parent https://dashboard.iatistandard.org/stats/current/aggregated/
wget -m --no-parent https://dashboard.iatistandard.org/stats/current/aggregated-publisher/$publisher_short_name/
wget -m --no-parent https://dashboard.iatistandard.org/stats/current/aggregated-file/$publisher_short_name/
wget -m --no-parent https://dashboard.iatistandard.org/stats/current/inverted-publisher/
wget -m --no-parent https://dashboard.iatistandard.org/stats/current/inverted-file/
wget -m --no-parent https://dashboard.iatistandard.org/stats/current/inverted-file-publisher/$publisher_short_name/
wget -m --no-parent https://dashboard.iatistandard.org/stats/gitaggregate-publisher-dated/$publisher_short_name/
mv dashboard.iatistandard.org/stats stats-calculated
for file in licenses.json gitdate.json; do
    curl --compressed https://dashboard.iatistandard.org/stats/$file > stats-calculated/$file
done
curl --compressed https://dashboard.iatistandard.org/stats/ckan.json | jq "{$publisher_short_name: .$publisher_short_name}" > stats-calculated/ckan.json

cat stats-calculated/current/inverted-publisher/activities.json  | jq "{$publisher_short_name: .$publisher_short_name}" > activities.json
mv activities.json stats-calculated/current/inverted-publisher/activities.json
rm stats-calculated/current/aggregated-publisher/*/index.html*
rm stats-calculated/current/aggregated-file/*/*/index.html*
