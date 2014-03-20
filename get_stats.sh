mkdir stats-calculated
for f in ckan gitdate; do
    curl --compress "http://arstneio.com/iati/stats/${f}.json" > stats-calculated/${f}.json
done

cd stats-calculated
wget "http://arstneio.com/iati/stats/current.tar.gz" -O current.tar.gz
wget "http://arstneio.com/iati/stats/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
tar -xvf current.tar.gz
tar -xvf gitaggregate-dated.tar.gz 

