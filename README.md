See the dashboard in action at http://bjwebb.github.io/IATI-Dashboard/

To install:

    # Set up a virtual environment
    virtualenv pyenv
    source pyenv/bin/activate
    pip install -r requirements.txt
    
    # Fetch the calculated stats
    git clone http://arstneio.com/iati/stats/.git stats-calculated

    mkdir out
    python fetch_data.py
    python plots.py
    python make_html.py

If you want to used the gh-pages branch as the output directory:

    git clone -b gh-pages git@github.com:Bjwebb/IATI-Dashboard.git out

Look into `git.sh` for doing the full update of an output git repository.
