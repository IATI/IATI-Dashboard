IATI Dashboard
==============

[![Coverage Status](https://coveralls.io/repos/github/IATI/IATI-Dashboard/badge.svg?branch=merge-codeforiati-and-publishingstats)](https://coveralls.io/github/IATI/IATI-Dashboard?branch=merge-codeforiati-and-publishingstats)
[![GPLv3 License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/IATI/IATI-Dashboard/blob/merge-codeforiati-and-publishingstats/LICENSE.md)

## Summary

 Product  |  IATI Dashboard
--- | ---
Description | A Django web application that provides key numbers, statistics and graphs about the data on the [IATI registry](http://iatiregistry.org/).  This repository is currently a development version where the IATI Dashboard/Publishing Statistics and Code for IATI Analytics are being merged.
Website |  Development only; see [IATI Dashboard](https://dashboard.iatistandard.org), and [Code for IATI Analytics](https://analytics.codeforiati.org) for live versions. 
Related | Repositories for the [live version of the IATI Dashboard](https://github.com/IATI/IATI-Dashboard), [live version of the IATI Publishing Stats](https://github.com/IATI/IATI-Publishing-Statistics), and [Code for IATI Analytics](https://github.com/codeforIATI/analytics).  Data is generated from [Code for IATI Stats](https://github.com/codeforIATI/IATI-Stats).
Documentation | Rest of README.md
Technical Issues | See https://github.com/IATI/IATI-Dashboard/issues
Support | https://iatistandard.org/en/guidance/get-support/

## High-level requirements

* Python 3.12
* Unix-based setup (e.g., Linux, MacOS X) with `bash`, `wget` and `curl` installed.
* Postgres database (see below for how to run this with docker)

## Running the app locally
### Overview
The IATI Dashboard is mostly written in Python but also has some helper Bash scripts to collect the data that the dashboard uses.  Top-level steps required to run the Dashboard are:

1. Setup Python environment and install dependencies.
2. Fetch the data.
3. Build the static graphs and other data that will be served via the Dashboard.
4. Run the web server.

### 1. Setup environment

Assuming that this repository has been cloned and you are in the root directory of the repository.

```
# Setup and activate a virtual environment (recommended)
python3.12 -m venv .ve
source .ve/bin/activate
```

Now install the dependencies.

```
pip install -r requirements.txt
```

### 2. Fetching the data

Bash scripts are used to fetch the data that the Dashboard will present.

```
# Fetch the necessary calculated stats
# This will store data in the ./stats-calculated directory
# These are created by https://github.com/IATI/IATI-Stats (see below for more information)
# This downloads ~1.5GB of data, which uncompresses to ~50GB
./get_stats.sh

# Fetch some extra data from github and github gists and other sources on the internet
# This will store data in the ./data directory
# This downloads ~60MB of data
./fetch_data.sh
```

### 3. Start Postgres database, run migrations, import data

```
docker run --name iati-dashboard-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=iati_dashboard -p 127.0.0.1:5432:5432 -d postgres:17
# Run this export command every time you open a new shell
export DATABASE_URL="postgres://postgres:postgres@localhost:5432/iati_dashboard"
python manage.py migrate
python manage.py dashboard_import
```


### 4. Build static data and graphs

```
python manage.py make_plots
python manage.py make_csv
```

### 5. Run the webserver.

```
DEBUG=True python manage.py runserver
```

The Dashboard will now be accessible from <http://localhost:8000/>.

### 6. Run the real-time changes background processor

```
python manage.py run_realtime_update_processor
```

This can be configured using the following environment variables:

```
REALTIME_UPDATE_SERVICE_LOOP_SLEEP=3  # optional, defaults to 3
REALTIME_UPDATE_SERVICE_LOOP_SLEEP_AFTER_ERROR=15   # optional, defaults to 15
AZ_SERVICE_BUS_CONNECTION_STRING=
AZ_SERVICE_BUS_REGISTRY_CHANGES_TOPIC_NAME=
AZ_SERVICE_BUS_REGISTRY_CHANGES_SUBSCRIPTION_NAME=
AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_TOPIC_NAME=
AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_SUBSCRIPTION_NAME=
```

The value of `AZ_SERVICE_BUS_CONNECTION_STRING` should be retreived from the
Azure portal.

The value of the other four variables should be drawn from the AsyncAPI
specification stored here: https://github.com/IATI/iati-message-queue-service.

## Development

### Automated tests
There are some unit tests written using `pytest` and site testing using Django's own testing framework.

Once the development dependencies have been installed the unit tests can be run with:

```
mkdir iati_dashboard/fixtures/
python manage.py dumpdata iati_dashboard.ReportingOrg > iati_dashboard/fixtures/reporting_orgs.json
pytest iati_dashboard
```

By default some tests are skipped because they depend on other services running. To run these:

```
DEBUG=True python manage.py runserver &
docker run -d -p 8888:8888 ghcr.io/validator/validator:latest
DASHBOARD_ROOT_URL=http://localhost:8000 pytest iati_dashboard
```

They can also be run against a deployed copy of the dashboard:

```
DASHBOARD_ROOT_URL=https://dashboard.iatistandard.org/ pytest iati_dashboard/tests/test_page_speed.py iati_dashboard/tests/test_validate_html.py
```

### Calculating your own statistics

The IATI Dashboard requires a `stats-calculated` directory, which can be downloaded using the `get_stats.sh` shell script as described above.  This can also be calculated using [Code for IATI Stats](http://github.com/codeforIATI/IATI-Stats) where `stats-calculated` corresponds to the `gitout` directory generated by [`git.sh` in IATI-Stats](https://github.com/codeforIATI/IATI-Stats#running-for-every-commit-in-the-data-directory).

Often you only want to regenerate the current stats, use `get_stats.sh` to download the pre-calculated historical stats and just replace the `stats-calculated/current directory` with the `out` directory produced by running the [loop, aggregate and invert commands individually](https://github.com/codeforIATI/IATI-Stats#getting-started), then regenerate graphs and CSV files as per the above.

### Adding new dependencies

If a change requires new dependencies then please add to `requirements.in` or `requirements_dev.in` as appropriate and recompile:

```
# Make sure you are in the virtualenv (see step 1 above)
source .ve/bin/activate
# Install an older version of pip, see https://github.com/jazzband/pip-tools/issues/2131
pip install --upgrade pip-tools 'pip<24.3'
pip-compile requirements.in
pip-compile requirements_dev.in
```

### Upgrading dependencies

```
# Make sure you are in the virtualenv (see step 1 above)
source .ve/bin/activate
# Install an older version of pip, see https://github.com/jazzband/pip-tools/issues/2131
pip install --upgrade pip-tools 'pip<24.3'
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements_dev.in
```

### Linting

Code linting is carried out using Black, isort and [Flake8](https://flake8.pycqa.org/en/latest/) and `pyproject.toml` has the configuration.

## License
    Copyright (C) 2013-2015 Ben Webb <bjwebb67@googlemail.com>
    Copyright (C) 2013-2014 David Carpenter <caprenter@gmail.com>
    Copyright (C) 2021 Andy Lulham <a.lulham@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
