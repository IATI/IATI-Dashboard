"""
Tests to be run on a predictable set of mock IATI data: end_to_end_tests/fixtures

See end_to_end_tests/README.md for more information.
"""

import pytest


@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.add_argument("-headless")
    return firefox_options


def test_home_page(selenium):
    selenium.get("http://localhost:8000/")
    assert "Dashboard Home" in selenium.find_element("tag name", "body").text
    selenium.find_element("link text", "Reporting Orgs").click()
    assert selenium.current_url.endswith("/publishers/")
    assert selenium.title == "IATI Dashboard – IATI Reporting Orgs"
    assert "Reporting orgs in query: 1" in selenium.find_element("tag name", "body").text
