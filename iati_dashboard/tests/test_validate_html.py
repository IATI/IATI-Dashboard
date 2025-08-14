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

    if page in [
        # files is too big to validate with the w3c validator when run from docker
        "files.html",
        "exploring-data/files/",
    ]:
        pytest.skip()

    r = requests.get(f"{dashboard_url}/{page}")
    html_validation = requests.post(
        "http://localhost:8888/?out=json", data=r.text, headers={"Content-Type": "text/html; charset=utf-8"}
    )
    assert all(message["type"] == "info" for message in html_validation.json()["messages"])
