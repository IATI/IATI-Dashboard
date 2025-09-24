#!/bin/bash
set -eux
# ^ https://explainshell.com/explain?cmd=set+-eux

publisher_short_name=zsl
domain=dev2.dashboard.iatistandard.org

if [ -d stats-calculated ]; then
    echo "stats-calculated directory already exists, exiting."
    exit
fi
wget -m --no-parent https://$domain/stats/current/bulk-data-service-metadata/
wget -m --no-parent https://$domain/stats/current/aggregated/
wget -m --no-parent https://$domain/stats/current/aggregated-publisher/$publisher_short_name/
wget -m --no-parent https://$domain/stats/current/aggregated-file/$publisher_short_name/
wget -m --no-parent https://$domain/stats/current/inverted-publisher/
wget -m --no-parent https://$domain/stats/current/inverted-file/
wget -m --no-parent https://$domain/stats/current/inverted-file-publisher/$publisher_short_name/
wget -m --no-parent https://$domain/stats/gitaggregate-publisher-dated/$publisher_short_name/
mv $domain/stats stats-calculated
for file in licenses.json gitdate.json; do
    curl --compressed https://$domain/stats/$file > stats-calculated/$file
done
curl --compressed https://$domain/stats/ckan.json | jq "{$publisher_short_name: .$publisher_short_name}" > stats-calculated/ckan.json

cp stats-calculated/current/bulk-data-service-metadata/reporting-orgs.json stats-calculated/current/bulk-data-service-metadata/reporting-orgs.json.all
cat stats-calculated/current/bulk-data-service-metadata/reporting-orgs.json.all | jq "{index_created, index_created_unix_timestamp, reporting_orgs: [.reporting_orgs[]|select(.short_name==\"$publisher_short_name\")]}" > stats-calculated/current/bulk-data-service-metadata/reporting-orgs.json
cp stats-calculated/current/bulk-data-service-metadata/datasets-full.json stats-calculated/current/bulk-data-service-metadata/datasets-full.json.all
cat stats-calculated/current/bulk-data-service-metadata/datasets-full.json.all | jq "{index_created, index_created_unix_timestamp, datasets: [.datasets[]|select(.reporting_org_short_name==\"$publisher_short_name\")]}" > stats-calculated/current/bulk-data-service-metadata/datasets-full.json

cat stats-calculated/current/inverted-publisher/activities.json  | jq "{$publisher_short_name: .$publisher_short_name}" > activities.json
mv activities.json stats-calculated/current/inverted-publisher/activities.json
rm stats-calculated/current/aggregated-publisher/*/index.html*
rm stats-calculated/current/aggregated-file/*/*/index.html*
