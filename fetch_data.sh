#!/bin/bash
mkdir data/downloads/
wget "https://gist.github.com/Bjwebb/8058775/raw/" -O data/downloads/history.csv
wget "https://gist.github.com/Bjwebb/6726204/raw/errors" -O data/downloads/errors
python fetch_data.py
