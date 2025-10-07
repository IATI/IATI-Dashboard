#!/bin/bash
# Run the end to end tests, including downloading the IATI-Stats repo,
# running the xml through that, then run the outputted stats through this repo.
# See end_to_end_tests/README.md for more information.

set -eux
# ^ https://explainshell.com/explain?cmd=set+-eux

# Temporarily turn off -x to make messages clearer
set +x
if [[ "$@" != "-f" ]]; then
    echo "This script will replace the IATI-Stats and stats-calculated directories with test data."
    echo "This script will also replace the database at \"$DATABASE_URL\" with test data."
    read -p "Do you wish to continue? (y/n): "
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
set -x

rm -rf IATI-Stats/ || true
git clone https://github.com/IATI/IATI-Stats

# Set up data
cp -r end_to_end_tests/fixtures/iati-data IATI-Stats/
cd IATI-Stats/iati-data
git init
git add .
git config user.email "test@example.com"
git config user.name "Test"
git commit -a -m "Initial commit"
cd ../..

# Run IATI-Stats
cd IATI-Stats
pip install -r requirements.txt
./git.sh
cd ..

# Run dashboard
rm -r stats-calculated || true
ln -s IATI-Stats/gitout stats-calculated
echo '{}' > stats-calculated/licenses.json
pip install -r requirements_dev.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py dashboard_import

# Kill all background processes when we exit, even when exiting with an error
trap 'kill $(jobs -p)' EXIT
python manage.py runserver &
pytest --driver Firefox end_to_end_tests/
