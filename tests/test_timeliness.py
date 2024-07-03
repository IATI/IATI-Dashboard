"""Testing of functions in timeliness.py
"""

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import timeliness  # noqa: E402


def test_short_month():
    month_strings = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    for index,s in enumerate(month_strings):
        assert timeliness.short_month('01-{:02d}-2024'.format(index+1)) == s
