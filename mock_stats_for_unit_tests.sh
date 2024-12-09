set -eux

mkdir stats-calculated
curl --compressed "https://dev.merged.dashboard.iatistandard.org/stats/ckan.json" > stats-calculated/ckan.json
mkdir -p stats-calculated/current/aggregated-publisher
mkdir -p stats-calculated/current/inverted-publisher
for f in activities codelist_values_by_major_version elements; do
    echo "{}" > stats-calculated/current/inverted-publisher/$f.json
done
