"""
Tests to be run on a predictable set of mock IATI data: end_to_end_tests/fixtures

See end_to_end_tests/README.md for more information.
"""

import pytest
import requests


@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.add_argument("-headless")
    return firefox_options


def test_home_page(selenium):
    root_url = "http://localhost:8000"

    selenium.get(root_url)
    assert "Dashboard Home" in selenium.find_element("tag name", "body").text

    selenium.get(f"{root_url}/errors/xml-errors/")
    xml_errors_body = selenium.find_element("tag name", "body").text
    selenium.get(f"{root_url}/errors/validation/")
    schema_validation_body = selenium.find_element("tag name", "body").text

    # Check that we're picking up bad xml and schema validation
    assert "test_ro_1-badxml" in xml_errors_body
    assert "test_ro_1-empty_activity" in schema_validation_body
    assert "test_ro_1-valid_activity" not in xml_errors_body
    assert "test_ro_1-valid_activity" not in schema_validation_body

    # Check that these activities validate against the schema,
    # so we know we've not typoed the elements/attributes we're interested in
    assert "in_ao_1-activities" not in xml_errors_body
    assert "in_ao_1-activities" not in schema_validation_body
    assert "in_ao_2-activities" not in xml_errors_body
    assert "in_ao_2-activities" not in schema_validation_body

    selenium.find_element("link text", "Reporting Orgs").click()
    assert selenium.current_url.endswith("/publishers/")

    # TODO click the interface to get to this page
    selenium.get(f"{root_url}/publishers/?recipient_country_code=AO")
    assert selenium.title == "IATI Dashboard – IATI Reporting Orgs"
    body_text = selenium.find_element("tag name", "body").text
    assert "Reporting orgs in query: 2" in body_text
    # Test recipient-country under iati-activity
    assert "in_ao_1" in body_text
    # Test recipient-country under transaction
    assert "in_ao_2" in body_text

    reporting_orgs = requests.get(f"{root_url}/api/reporting-orgs/?format=json&recipient_country_code=AO").json()[
        "results"
    ]
    assert {ro["short_name"] for ro in reporting_orgs} == {"in_ao_1", "in_ao_2"}
