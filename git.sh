cd out
git reset --hard HEAD
git pull
rm -r *
cd ..
./fetch_data.sh || exit 1
python plots.py || exit 1
python make_html.py || exit 1
cp favicon.png out/
cd out
git add .
git commit -a -m 'Auto'
git push
