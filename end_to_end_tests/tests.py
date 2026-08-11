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


root_url = "http://localhost:8000"


def test_home_page(selenium):
    selenium.get(root_url)
    assert "Dashboard Home" in selenium.find_element("tag name", "body").text


def test_downloads_errors(selenium):
    selenium.get(f"{root_url}/errors/download-errors/")
    tr = selenium.find_element("tag name", "table").find_element("tag name", "tbody").find_element("tag name", "tr")
    assert "no_successful_downloads-dataset1" in tr.text
    assert "http_non_200" in tr.text
    assert "404" in tr.text


def test_downloads_errors_csv():
    with open("end_to_end_tests/fixtures/download-errors.csv", "rb") as fp:
        assert requests.get(f"{root_url}/errors/download-errors.csv").content == fp.read()


def test_errors(selenium):
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


def get_cell(table, row_id_th_text, row_id, cell_th_text):
    ths = [th.text for th in table.find_elements("tag name", "th")]
    assert len(ths) > 0

    row_id_index = ths.index(row_id_th_text)
    for tr in table.find_elements("tag name", "tr"):
        try:
            if tr.find_elements("tag name", "td")[row_id_index].text == row_id:
                break
        except IndexError:
            continue
    else:
        raise Exception("No row matched")

    cell_index = ths.index(cell_th_text)
    return tr.find_elements("tag name", "td")[cell_index]


def test_reporting_orgs(selenium):
    selenium.get(root_url)
    selenium.find_element("link text", "Reporting Orgs").click()
    assert selenium.current_url.endswith("/publishers/")

    table = selenium.find_element("css selector", ".iati-table")
    hq_country_cell = get_cell(table, "REPORTING ORG SHORT NAME", "test_ro_1", "HQ COUNTRY")
    assert hq_country_cell.text == "ES"
    assert hq_country_cell.find_element("tag name", "abbr").get_attribute("title") == "Spain"

    table = selenium.find_element("css selector", ".iati-table")
    recipient_countries_cell = get_cell(table, "REPORTING ORG SHORT NAME", "in_ao_1", "RECIPIENT COUNTRIES")
    assert recipient_countries_cell.text == "1"
    href = recipient_countries_cell.find_element("tag name", "a").get_attribute("href")
    assert href.endswith("/publishers/in_ao_1/#p_countries")

    selenium.get(href)

    recipient_countries_panel = selenium.find_element("css selector", "#p_countries")
    assert "Recipient Countries" in recipient_countries_panel.text
    assert "AO" in recipient_countries_panel.text
    assert "Angola" in recipient_countries_panel.text

    source_url_1 = selenium.find_element("link text", "Source Url")
    assert source_url_1.get_attribute("href") == "http://example.com/1"


def test_reporting_orgs_filter(selenium):
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
