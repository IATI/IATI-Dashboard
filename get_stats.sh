mkdir stats-calculated
for f in gitaggregate-dated ckan gitdate; do
    curl --compress "http://arstneio.com/iati/stats/${f}.json" > stats-calculated/${f}.json
done

cd stats-calculated
wget "http://arstneio.com/iati/stats/current.tar.gz" -O current.tar.gz
tar -xvf current.tar.gz
