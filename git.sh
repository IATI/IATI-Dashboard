cd out
git reset --hard HEAD
git pull
rm -r *
cd ..
./fetch_data.sh
python plots.py
python make_html.py
cp favicon.png out/
cd out
git add .
git commit -a -m 'Auto'
git push
