mkdir stats-calculated
for f in gitaggregate-dated ckan gitdate; do
    curl --compress "http://arstneio.com/iati/stats/${f}.json" > stats-calculated/${f}.json
done

mkdir stats-calculated/current
for f in aggregated inverted inverted-file; do
    curl --compress "http://arstneio.com/iati/stats/current/${f}.json" > stats-calculated/current/${f}.json
done
