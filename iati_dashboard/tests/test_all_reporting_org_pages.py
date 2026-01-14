import os

import pytest
import requests

if "DASHBOARD_ROOT_URL" in os.environ:
    dashboard_url = os.environ["DASHBOARD_ROOT_URL"]
    reporting_orgs = requests.get(f"{dashboard_url}/api/reporting-orgs?page_size=1000000000").json()
    short_names = [reporting_org["short_name"] for reporting_org in reporting_orgs["results"]]
else:
    pytest.skip(allow_module_level=True)


@pytest.mark.parametrize("short_name", short_names)
def test_page_speed(short_name):
    r = requests.get(f"{dashboard_url}/publishers/{short_name}")
    assert r.status_code == 200
    assert r.elapsed.total_seconds() < 2
