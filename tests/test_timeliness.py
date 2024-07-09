"""Testing of functions in timeliness.py
"""

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import timeliness  # noqa: E402


def test_short_month():
    month_strings = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for index, s in enumerate(month_strings):
        assert timeliness.short_month('01-{:02d}-2024'.format(index + 1)) == s

def test_parse_iso_date():
    test_date_1 = timeliness.parse_iso_date("2024-01-01")
    assert test_date_1.year==2024
    assert test_date_1.month==1
    assert test_date_1.day==1

    test_date_2 = timeliness.parse_iso_date("2024-02-29")
    assert test_date_2.year==2024
    assert test_date_2.month==2
    assert test_date_2.day==29

    test_date_3 = timeliness.parse_iso_date("2024-04-01")
    assert test_date_3.year==2024
    assert test_date_3.month==4
    assert test_date_3.day==1
