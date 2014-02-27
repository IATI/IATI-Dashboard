IATI Dashboard
==============

The IATI dashboard is a displays key numbers and graphs about the data on the IATI registry.

See the dashboard in action at http://iati.github.io/IATI-Dashboard/

The dashboard is in beta, all contents/urls/machine readable downloads are subject to change.

Technology Overview
^^^^^^^^^^^^^^^^^^^

The dashboard is written in Python.

``make_html.py`` contains is a Flask application that makes use of Frozen Flask to generate some static HTML that is then deployed to github pages. 

``plots.py`` generates static images of graphs using matplotlib.

The dashboard uses various data from github, that can be fetched using ``fetch_data.sh``, and some stats calculated on IATI data, using code in the `IATI-Stats repository <https://github.com/IATI/IATI-Stats>`_. ``get_stats.sh`` can be used to fetch nightly calculated stats.

Installation
^^^^^^^^^^^^

Requirements:

* Unix based setup (e.g. Linux, Mac OS X) with bash etc.
* Python 2.7
* python-virtualenv (optional)
* Development files for libfreetype and libpng e.g. `libfreetype6-dev libpng-dev`

To install:

.. code-block:: bash

    ## Set up a virtual environment (recommended)
    # Create a virtual environment
    virtualenv pyenv
    # Active the virtual environment
    # (you need to this every time you open a new terminal session)
    source pyenv/bin/activate

    ## Install python dependencies
    ## Use pip as described below, or your distro's package manager to install
    ## the dependcies in requirements.txt
    # If you are running a less recent linux distro, you will need to install distribute
    easy_install -U distribute
    pip install -r requirements.txt

    # Create a configuration file
    cp config.py.example config.py # And provide the necessary values
    
    # Fetch the necessary calculated stats
    ./get_stats.sh
    # Fetch some extra data from github and github gists
    ./fetch_data.sh

    mkdir out
    python plots.py
    python make_html.py

If you want to used the gh-pages branch as the output directory:

.. code-block:: bash

    git clone -b gh-pages git@github.com:Bjwebb/IATI-Dashboard.git out

Look into ``git.sh`` for doing the full update of an output git repository.

Development
^^^^^^^^^^^

For development, you can use the live Flask development server, instead of Frozen Flask.

.. code-block:: bash

    python make_html --live

License
^^^^^^^

::

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
