# IATI Dashboard

See the dashboard in action at http://iati.github.io/IATI-Dashboard/

## Installation

Requirements:

* Unix based setup (e.g. Linux, Mac OS X) with bash etc.
* Python 2.7
* python-virtualenv
* Development files for libfreetype and libpng e.g. `libfreetype6-dev libpng-dev`

To install:

    # Set up a virtual environment
    virtualenv pyenv
    source pyenv/bin/activate
    # If you are running a less recent linux distro, you will need to install distribute
    easy_install -U distribute
    pip install -r requirements.txt
    
    # Fetch the necessary calculated stats
    ./get_stats.sh
    # Fetch some extra data from github and github gists
    ./fetch_data.py

    mkdir out
    python plots.py
    python make_html.py

If you want to used the gh-pages branch as the output directory:

    git clone -b gh-pages git@github.com:Bjwebb/IATI-Dashboard.git out

Look into `git.sh` for doing the full update of an output git repository.

## License
```
Copyright (C) 2013 Ben Webb <bjwebb67@googlemail.com>
Copyright (C) 2013 David Carpenter <caprenter@gmail.com>

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
```
