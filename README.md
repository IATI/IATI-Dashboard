See the dashboard in action at http://bjwebb.github.io/IATI-Dashboard/

To install:

    # Set up a virtual environment
    virtualenv pyenv
    source pyenv/bin/activate
    pip install -r requirements.txt
    
    # Fetch the necessary calculated stats
    ./get_stats.sh

    mkdir out
    python fetch_data.py
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
