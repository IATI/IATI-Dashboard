import os

import pytest
import requests

from .test_page_speed import EXAMPLE_PAGES


@pytest.mark.parametrize("page", EXAMPLE_PAGES)
def test_validate_html(page):
    if "DASHBOARD_ROOT_URL" in os.environ:
        dashboard_url = os.environ["DASHBOARD_ROOT_URL"]
    else:
        pytest.skip()

    # Skip non html page
    if page.endswith(".json"):
        pytest.skip()
    # Skip those pages we know don't validate
    # The plan is to fix them and then remove these
    # https://github.com/IATI/IATI-Dashboard/issues/735
    if page.startswith("publishing-statistics/"):
        pytest.skip()
    if page.endswith(".html"):
        pytest.skip()
    if page in [
        "exploring-data/files/",
        "exploring-data/elements/iati-activity_activity-date_@iso-date/",
        "exploring-data/versions/",
    ]:
        pytest.skip()

    r = requests.get(f"{dashboard_url}/{page}")
    html_validation = requests.post(
        "http://localhost:8888/?out=json", data=r.text, headers={"Content-Type": "text/html; charset=utf-8"}
    )
    assert len(html_validation.json()["messages"]) == 0
