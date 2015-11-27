echo "Removing 'out' directory and creating a new one"
rm -rf out
mkdir out

echo "Fetching data"
./fetch_data.sh &> fetch_data.log || exit 1

echo "Running plots.py"
python plots.py || exit 1

echo "make_csv.py"
python make_csv.py || exit 1

echo "speakers kit.py"
python speakers_kit.py || exit 1

echo "make_html.py"
python make_html.py || exit 1

echo "Copying favicon and moving to the web directory"
cp static/img/favicon.png out/
mv web web.1
mv out web
rm -rf web.1
