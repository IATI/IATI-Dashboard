mkdir stats-calculated
for f in ckan gitdate; do
    curl --compress "http://dashboard.iatistandard.org/stats/${f}.json" > stats-calculated/${f}.json
done

cd stats-calculated
wget "http://dashboard.iatistandard.org/stats/current.tar.gz" -O current.tar.gz
wget "http://dashboard.iatistandard.org/stats/gitaggregate-dated.tar.gz" -O gitaggregate-dated.tar.gz
tar -xvf current.tar.gz
tar -xvf gitaggregate-dated.tar.gz 

