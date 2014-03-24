rm -rf out
mkdir out
./fetch_data.sh || exit 1
python plots.py || exit 1
python make_csv.py || exit 1
python make_html.py || exit 1
cp favicon.png out/
mv web web.1
mv out web
rm -rf web.1
