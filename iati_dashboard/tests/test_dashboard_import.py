import importlib
import os
import uuid

import pytest
from django.core.management import call_command

import iati_dashboard
from iati_dashboard import filepaths, models


@pytest.mark.django_db
def test_dashboard_import_metadata_reporting_orgs():
    id1 = uuid.UUID("297649cc-0933-4c74-8df7-9ac27e6f4680")
    ro1 = models.ReportingOrg(id=id1, short_name="test_ro_1", stats_json={"test_key": "test_value"})
    ro1.save()
    # Check this isn't populated yet, so we know it's populated in the import
    assert "hq_country" not in ro1.metadata_json
    ro2 = models.ReportingOrg(id="8a583e50-9ab9-48d1-9ac3-3bcef9678ba2", short_name="test_ro_2")
    ro2.save()

    call_command("dashboard_import_metadata", "iati_dashboard/tests/fixtures/metadata/")

    id3 = uuid.UUID("36410008-48a5-4f1a-938c-972d549de3ed")
    assert set(models.ReportingOrg.objects.values_list("id", flat=True)) == {id1, id3}
    ro1_again = models.ReportingOrg.objects.get(short_name="test_ro_1")
    assert ro1_again.stats_json["test_key"] == "test_value"
    assert ro1_again.metadata_json["hq_country"] == "ES"


@pytest.mark.django_db
def test_dashboard_import_metadata_datasets():
    ro1 = models.ReportingOrg(uuid.UUID("297649cc-0933-4c74-8df7-9ac27e6f4680"), short_name="test_ro_1")
    id1 = uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    d1 = models.Dataset(id=id1, short_name="test_ro_1-d1", reporting_org=ro1, stats_json={"test_key": "test_value"})
    d1.save()
    # Check this isn't populated yet, so we know it's populated in the import
    assert "source_url" not in d1.metadata_json
    d2 = models.Dataset(id="7626aebd-ee1a-473f-ae6d-c8f25a41d392", short_name="test_ro_1-d2", reporting_org=ro1)
    d2.save()

    call_command("dashboard_import_metadata", "iati_dashboard/tests/fixtures/metadata/")

    id3 = uuid.UUID("45adaebd-93f4-452e-b011-fc4f6e02882c")
    assert set(models.Dataset.objects.values_list("id", flat=True)) == {id1, id3}
    d1_again = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert d1_again.stats_json["test_key"] == "test_value"
    assert d1_again.metadata_json["source_url"] == "http://example.com/3"


@pytest.mark.django_db
def test_dashboard_import_metadata_reporting_orgs_duplicate_short_name(settings):
    """
    This is the case where a reporting org short name appears in the database, and the metadata file being processed, with different IDs.
    """

    old_id1 = uuid.UUID("bd694e32-6ffe-43ef-9873-45f7afa6d739")
    old_ro1 = models.ReportingOrg(id=old_id1, short_name="test_ro_1", stats_json={"test_key": "test_value"})
    old_ro1.save()

    call_command("dashboard_import_metadata", "iati_dashboard/tests/fixtures/metadata/")

    new_id1 = uuid.UUID("297649cc-0933-4c74-8df7-9ac27e6f4680")
    ids = set(models.ReportingOrg.objects.values_list("id", flat=True))
    assert old_id1 not in ids
    assert new_id1 in ids
    new_ro1 = models.ReportingOrg.objects.get(short_name="test_ro_1")
    assert new_ro1.id != old_id1
    assert new_ro1.id == new_id1
    # We don't expect the stats to persist when the ID has changed like this
    assert new_ro1.stats_json.get("test_key") != "test_value"
    assert new_ro1.metadata_json["hq_country"] == "ES"


@pytest.mark.django_db
def test_dashboard_import_metadata_datasets_duplicate_short_name(settings):
    """
    This is the case where a dataset short name appears in the database, and the metadata file being processed, with different IDs.
    """

    ro1 = models.ReportingOrg(uuid.UUID("297649cc-0933-4c74-8df7-9ac27e6f4680"), short_name="test_ro_1")
    old_id1 = uuid.UUID("4dff1253-616d-47f8-9bf1-b6251efa3805")
    old_d1 = models.Dataset(
        id=old_id1, short_name="test_ro_1-d1", reporting_org=ro1, stats_json={"test_key": "test_value"}
    )
    old_d1.save()

    call_command("dashboard_import_metadata", "iati_dashboard/tests/fixtures/metadata/")

    new_id1 = uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    ids = set(models.Dataset.objects.values_list("id", flat=True))
    assert old_id1 not in ids
    assert new_id1 in ids
    new_d1 = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert new_d1.id != old_id1
    assert new_d1.id == new_id1
    # We don't expect the stats to persist when the ID has changed like this
    assert new_d1.stats_json.get("test_key") != "test_value"
    assert new_d1.metadata_json["source_url"] == "http://example.com/3"


def join_stats_path_fixture(p: str) -> str:
    return os.path.join("iati_dashboard/tests/fixtures/stats-calculated/", p)


@pytest.mark.django_db
def test_dashboard_import_stats_not_found(capsys, monkeypatch):
    """
    If we run the stats import without having done the metadata import, it won't work, and will give us not found messages.
    """

    monkeypatch.setattr(filepaths, "join_stats_path", join_stats_path_fixture)
    # We need to do this because data.py imports the stats JSON at import time
    importlib.reload(iati_dashboard.data)

    assert models.ReportingOrg.objects.count() == 0
    assert models.Dataset.objects.count() == 0

    call_command("dashboard_import_stats")

    captured = capsys.readouterr()
    assert models.ReportingOrg.objects.count() == 0
    assert models.Dataset.objects.count() == 0
    assert captured.err == ""
    assert captured.out == """Reporting Org 297649cc-0933-4c74-8df7-9ac27e6f4680 (test_ro_1), not found
Dataset 24d5d96c-8b36-482e-9c1a-d6ffeb46f9b2 (test_ro_1-valid_activity), not found
"""


@pytest.mark.django_db
def test_dashboard_import_stats_successful(capsys, monkeypatch):
    monkeypatch.setattr(filepaths, "join_stats_path", join_stats_path_fixture)
    # We need to do this because data.py imports the stats JSON at import time
    importlib.reload(iati_dashboard.data)
    importlib.reload(iati_dashboard.comprehensiveness)

    assert models.ReportingOrg.objects.count() == 0
    assert models.Dataset.objects.count() == 0

    call_command("dashboard_import_metadata")
    call_command("dashboard_import_stats")

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""
    assert models.ReportingOrg.objects.count() == 1
    assert models.ReportingOrg.objects.first().stats_json["activities"] == 1
    assert models.Dataset.objects.count() == 1
    assert models.Dataset.objects.first().stats_json["activities"] == 1
