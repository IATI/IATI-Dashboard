import copy
import datetime
import json
import shutil
import uuid

import pytest
from django.core.management import call_command

from iati_dashboard import models
from iati_dashboard.realtime_message_processor.message_processor import MessageProcessor

MESSAGE_PROCESSOR_CONFIG_FIXTURE = {
    "REALTIME_UPDATE_SERVICE_LOOP_SLEEP": None,
    "REALTIME_UPDATE_SERVICE_LOOP_SLEEP_AFTER_ERROR": None,
    "AZ_SERVICE_BUS_CONNECTION_STRING": None,
    "AZ_SERVICE_BUS_REGISTRY_CHANGES_TOPIC_NAME": None,
    "AZ_SERVICE_BUS_REGISTRY_CHANGES_SUBSCRIPTION_NAME": None,
    "AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_TOPIC_NAME": None,
    "AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_SUBSCRIPTION_NAME": None,
}


MESSAGE_PAYLOAD_DATASET_UPDATED_FIXTURE = {
    "dataset": {
        "id": "e9f8b60d-dfdb-419b-9902-bb683287e49f",
        "short_name": "test_ro_1-d1renamed",
        "source_type": "primary_source",
        "licence_id": "cc-by",
        "visibility": "public",
        "url": "http://www.example.com/dataset",
        "last_url_update_date": "",
        "last_metadata_update_date": "",
        "reporting_org_id": "297649cc-0933-4c74-8df7-9ac27e6f4680",
        "reporting_org_short_name": "test_ro_1",
    },
    "dataset_actions": [
        {
            "id": "989596f2-81ee-f1a7-92a3-699dd2625665",
            "dataset_id": "4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8",
            "action_type": "update_metadata",
            "created_date": "2026-02-24 16:30:04",
            "responsible_org_id": "a4133505-eb55-42d6-9c54-582dd21c7014",
            "responsible_org_name": "Open Data Services",
            "user_application_id": "cb8e551b-c1d5-46bc-a769-5c1ea38caad3",
            "user_application_name": "IATI Account",
            "user_name": "Test User",
            "user_id": "560e0f39-829a-6d50-7505-69490018773f",
        }
    ],
    "message_type": "DATASET_UPDATED",
    "message_date": "2026-06-24T16:30:04+00:00",
}


MESSAGE_PAYLOAD_DATASET_CHECK_RESULT_FIXTURE = {
    "dataset_check_result": {
        "id": "e9f8b60d-dfdb-419b-9902-bb683287e49f",
        "short_name": "test_ro_1-d1renamed",
        "licence_id": "cc-by",
    },
    "message_type": "DATASET_CHECK_RESULT",
    "message_date": "2026-06-24T16:30:04+00:00",
}


@pytest.mark.django_db
def test_dashboard_import_and_message_processor_metadata_json(tmpdir):
    # Copy metadata fixture to a temporary directory, because we will edit it
    shutil.copytree("iati_dashboard/tests/fixtures/metadata/", tmpdir.join("metadata"))

    # Import some initial metadata
    with open(tmpdir.join("metadata").join("datasets-full.json")) as fp:
        datasets_full = json.load(fp)
        datasets_full["index_created"] = "2026-06-26 16:00:00+00:00"
    with open(tmpdir.join("metadata").join("datasets-full.json"), "w") as fp:
        json.dump(datasets_full, fp)
    call_command("dashboard_import_metadata", tmpdir.join("metadata"))
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.licence_id == "cc-zero" and dataset.metadata_json["licence_id"] == "cc-zero"
    assert dataset.metadata_json_datetime == datetime.datetime(2026, 6, 26, 16, 0, tzinfo=datetime.timezone.utc)
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1renamed")

    # If the message processor has an earlier datetime, nothing will be done
    message_processor = MessageProcessor(MESSAGE_PROCESSOR_CONFIG_FIXTURE)
    message_payload = copy.deepcopy(MESSAGE_PAYLOAD_DATASET_UPDATED_FIXTURE)
    message_payload["message_date"] = "2026-06-26T15:00:00+00:00"
    message_processor.process_registry_dataset_updated(message_payload)
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.licence_id == "cc-zero" and dataset.metadata_json["licence_id"] == "cc-zero"
    assert dataset.metadata_json_datetime == datetime.datetime(2026, 6, 26, 16, 0, tzinfo=datetime.timezone.utc)
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1renamed")

    # If the message processor has a later datetime, an update will happen
    message_processor = MessageProcessor(MESSAGE_PROCESSOR_CONFIG_FIXTURE)
    message_payload = copy.deepcopy(MESSAGE_PAYLOAD_DATASET_UPDATED_FIXTURE)
    message_payload["message_date"] = "2026-06-26T17:00:00+00:00"
    message_processor.process_registry_dataset_updated(message_payload)
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1")
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1renamed")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.licence_id == "cc-by" and dataset.metadata_json["licence_id"] == "cc-by"
    assert dataset.metadata_json_datetime == datetime.datetime(2026, 6, 26, 17, 0, tzinfo=datetime.timezone.utc)

    # If we run metadata import with an earlier datetime than the message processor, nothing should happen to this dataset
    with open(tmpdir.join("metadata").join("datasets-full.json")) as fp:
        datasets_full = json.load(fp)
        datasets_full["index_created"] = "2026-06-26 16:30:00+00:00"
    with open(tmpdir.join("metadata").join("datasets-full.json"), "w") as fp:
        json.dump(datasets_full, fp)
    call_command("dashboard_import_metadata", tmpdir.join("metadata"))
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1")
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1renamed")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.licence_id == "cc-by" and dataset.metadata_json["licence_id"] == "cc-by"
    assert dataset.metadata_json_datetime == datetime.datetime(2026, 6, 26, 17, 0, tzinfo=datetime.timezone.utc)

    # If we run metadata import with a latesr datetime than the message processor, we should get an update
    with open(tmpdir.join("metadata").join("datasets-full.json")) as fp:
        datasets_full = json.load(fp)
        datasets_full["index_created"] = "2026-06-26 19:00:00+00:00"
    with open(tmpdir.join("metadata").join("datasets-full.json"), "w") as fp:
        json.dump(datasets_full, fp)
    call_command("dashboard_import_metadata", tmpdir.join("metadata"))
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.licence_id == "cc-zero" and dataset.metadata_json["licence_id"] == "cc-zero"
    assert dataset.metadata_json_datetime == datetime.datetime(2026, 6, 26, 19, 0, tzinfo=datetime.timezone.utc)
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1renamed")


@pytest.mark.django_db
def test_dashboard_import_and_message_processor_check_result(tmpdir):
    # Copy metadata fixture to a temporary directory, because we will edit it
    shutil.copytree("iati_dashboard/tests/fixtures/metadata/", tmpdir.join("metadata"))

    # Import some initial metadata
    with open(tmpdir.join("metadata").join("datasets-full.json")) as fp:
        datasets_full = json.load(fp)
        datasets_full["index_created"] = "2026-06-26 16:00:00+00:00"
    with open(tmpdir.join("metadata").join("datasets-full.json"), "w") as fp:
        json.dump(datasets_full, fp)
    call_command("dashboard_import_metadata", tmpdir.join("metadata"))
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.check_result_json["licence_id"] == "cc-zero"
    assert dataset.check_result_json_datetime == datetime.datetime(2026, 6, 26, 16, 0, tzinfo=datetime.timezone.utc)
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1renamed")

    # If the message processor has an earlier datetime, nothing will be done
    message_processor = MessageProcessor(MESSAGE_PROCESSOR_CONFIG_FIXTURE)
    message_payload = copy.deepcopy(MESSAGE_PAYLOAD_DATASET_CHECK_RESULT_FIXTURE)
    message_payload["message_date"] = "2026-06-26T15:00:00+00:00"
    message_processor.process_dataset_check_result_updated(message_payload)
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.licence_id == "cc-zero" and dataset.metadata_json["licence_id"] == "cc-zero"
    assert dataset.check_result_json_datetime == datetime.datetime(2026, 6, 26, 16, 0, tzinfo=datetime.timezone.utc)
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1renamed")

    # If the message processor has a later datetime, an update will happen
    message_processor = MessageProcessor(MESSAGE_PROCESSOR_CONFIG_FIXTURE)
    message_payload = copy.deepcopy(MESSAGE_PAYLOAD_DATASET_CHECK_RESULT_FIXTURE)
    message_payload["message_date"] = "2026-06-26T17:00:00+00:00"
    message_processor.process_dataset_check_result_updated(message_payload)
    # Unlike DATASET_UPDATED we don't expect the short name to change
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1renamed")
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.check_result_json["licence_id"] == "cc-by"
    # Explain this
    assert dataset.licence_id == "cc-zero"
    assert dataset.check_result_json_datetime == datetime.datetime(2026, 6, 26, 17, 0, tzinfo=datetime.timezone.utc)

    # If we run metadata import with an earlier datetime than the message processor, nothing should happen to this dataset
    with open(tmpdir.join("metadata").join("datasets-full.json")) as fp:
        datasets_full = json.load(fp)
        datasets_full["index_created"] = "2026-06-26 16:30:00+00:00"
    with open(tmpdir.join("metadata").join("datasets-full.json"), "w") as fp:
        json.dump(datasets_full, fp)
    call_command("dashboard_import_metadata", tmpdir.join("metadata"))
    # Unlike DATASET_UPDATED we don't expect the short name to change
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1reanmed")
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.check_result_json["licence_id"] == "cc-by"
    assert dataset.check_result_json_datetime == datetime.datetime(2026, 6, 26, 17, 0, tzinfo=datetime.timezone.utc)

    # If we run metadata import with a latesr datetime than the message processor, we should get an update
    with open(tmpdir.join("metadata").join("datasets-full.json")) as fp:
        datasets_full = json.load(fp)
        datasets_full["index_created"] = "2026-06-26 19:00:00+00:00"
    with open(tmpdir.join("metadata").join("datasets-full.json"), "w") as fp:
        json.dump(datasets_full, fp)
    call_command("dashboard_import_metadata", tmpdir.join("metadata"))
    dataset = models.Dataset.objects.get(short_name="test_ro_1-d1")
    assert dataset.id == uuid.UUID("e9f8b60d-dfdb-419b-9902-bb683287e49f")
    assert dataset.check_result_json["licence_id"] == "cc-zero"
    assert dataset.check_result_json_datetime == datetime.datetime(2026, 6, 26, 19, 0, tzinfo=datetime.timezone.utc)
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="test_ro_1-d1renamed")
