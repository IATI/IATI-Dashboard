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

echo "Copying static elements"
cp static/img/favicon.png out/
cp static/img/tablesorter-icons.gif out/

echo "Make a backup of the old web directory and make new content live"
rsync -a --delete web web.bk
mv web web.1
mv out web
rm -rf web.1
