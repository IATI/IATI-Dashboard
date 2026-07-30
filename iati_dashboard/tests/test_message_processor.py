import datetime

import pytest

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


@pytest.mark.django_db
@pytest.mark.parametrize("visibility", ["public", "private"])
def test_dataset_created(visibility):
    reporting_org = models.ReportingOrg(id="a4133505-eb55-42d6-9c54-582dd21c7014", short_name="odsc")
    reporting_org.save()

    message_processor = MessageProcessor(MESSAGE_PROCESSOR_CONFIG_FIXTURE)
    message_payload = {
        "dataset": {
            "id": "4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8",
            "short_name": "ods-sample-2",
            "source_type": "primary_source",
            "licence_id": "cc-by",
            "visibility": visibility,
            "url": "http://www.example.com/dataset",
            "last_url_update_date": "",
            "last_metadata_update_date": "",
            "reporting_org_id": "a4133505-eb55-42d6-9c54-582dd21c7014",
            "reporting_org_short_name": "odsc",
        },
        "dataset_actions": [
            {
                "id": "989596f2-81ee-f1a7-92a3-699dd2625665",
                "dataset_id": "4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8",
                "action_type": "create",
                "created_date": "2026-02-24 16:30:04",
                "responsible_org_id": "a4133505-eb55-42d6-9c54-582dd21c7014",
                "responsible_org_name": "Open Data Services",
                "user_application_id": "cb8e551b-c1d5-46bc-a769-5c1ea38caad3",
                "user_application_name": "IATI Account",
                "user_name": "Test User",
                "user_id": "560e0f39-829a-6d50-7505-69490018773f",
            }
        ],
        "message_type": "DATASET_CREATED",
        "message_date": "2026-02-24T16:30:04+00:00",
    }
    message_processor.dispatch_event("DATASET_CREATED", message_payload)

    if visibility == "public":
        dataset = models.Dataset.objects.get(short_name="ods-sample-2")

        assert str(dataset.id) == "4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8"
        assert dataset.short_name == "ods-sample-2"
        assert dataset.source_url == "http://www.example.com/dataset"
        assert dataset.metadata_json_datetime == datetime.datetime(
            2026, 2, 24, 16, 30, 4, tzinfo=datetime.timezone.utc
        )

        assert "activities" in dataset.stats_json
        assert "organisations" in dataset.stats_json
        assert "activity_files" in dataset.stats_json
        assert "organisation_files" in dataset.stats_json
        assert "file_size" in dataset.stats_json
        assert "hierarchies" in dataset.stats_json
        assert "reporting_orgs" in dataset.stats_json

    else:
        assert models.Dataset.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("visibility", ["public", "private"])
def test_dataset_updated(visibility):
    reporting_org = models.ReportingOrg(id="a4133505-eb55-42d6-9c54-582dd21c7014", short_name="odsc")
    reporting_org.save()

    dataset = models.Dataset(
        id="923475e1-2ee7-0d71-b0a8-69f3686a7fee", short_name="ods-test-11", reporting_org=reporting_org
    )
    dataset.save()
    assert models.Dataset.objects.count() == 1

    message_processor = MessageProcessor(MESSAGE_PROCESSOR_CONFIG_FIXTURE)
    message_payload = {
        "dataset": {
            "id": "923475e1-2ee7-0d71-b0a8-69f3686a7fee",
            "short_name": "ods-test-11",
            "source_type": "secondary_source",
            "licence_id": "cc-by-sa",
            "visibility": visibility,
            "url": "http://example.com/dataset2",
            "last_url_update_date": "2026-05-26T12:18:07+00:00",
            "last_metadata_update_date": "",
            "reporting_org_id": "a4133505-eb55-42d6-9c54-582dd21c7014",
            "reporting_org_short_name": "odsc",
        },
        "dataset_actions": [
            {
                "id": "115e65dd-75a5-b37f-4979-6a158fcf0a5e",
                "dataset_id": "923475e1-2ee7-0d71-b0a8-69f3686a7fee",
                "action_type": "update_metadata",
                "created_date": "2026-05-26 12:18:07",
                "responsible_org_id": "a4133505-eb55-42d6-9c54-582dd21c7014",
                "responsible_org_name": "Open Data Services",
                "user_application_id": "cb8e551b-c1d5-46bc-a769-5c1ea38caad3",
                "user_application_name": "IATI Account",
                "user_name": "SK Test08",
                "user_id": "560e0f39-829a-6d50-7505-69490018773f",
            }
        ],
        "message_type": "DATASET_UPDATED",
        "message_date": "2026-05-26T12:18:07+00:00",
    }
    message_processor.dispatch_event("DATASET_UPDATED", message_payload)

    if visibility == "public":
        dataset = models.Dataset.objects.get(short_name="ods-test-11")

        assert str(dataset.id) == "923475e1-2ee7-0d71-b0a8-69f3686a7fee"
        assert dataset.short_name == "ods-test-11"
        assert dataset.source_url == "http://example.com/dataset2"
        assert dataset.metadata_json_datetime == datetime.datetime(
            2026, 5, 26, 12, 18, 7, tzinfo=datetime.timezone.utc
        )
    else:
        assert models.Dataset.objects.count() == 0


@pytest.mark.django_db
def test_dataset_deleted():
    reporting_org = models.ReportingOrg(id="a4133505-eb55-42d6-9c54-582dd21c7014", short_name="odsc")
    reporting_org.save()

    dataset = models.Dataset(
        id="4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8", short_name="ods-sample-2", reporting_org=reporting_org
    )
    dataset.save()
    assert models.Dataset.objects.count() == 1

    message_processor = MessageProcessor(MESSAGE_PROCESSOR_CONFIG_FIXTURE)
    message_payload = {
        "dataset": {
            "id": "4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8",
            "short_name": "ods-sample-2",
            "source_type": "primary_source",
            "licence_id": "cc-by",
            "visibility": "private",
            "url": "http://www.example.com/dataset",
            "last_url_update_date": "",
            "last_metadata_update_date": "",
            "reporting_org_id": "a4133505-eb55-42d6-9c54-582dd21c7014",
            "reporting_org_short_name": "odsc",
        },
        "dataset_actions": [
            {
                "id": None,
                "dataset_id": "4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8",
                "action_type": "delete",
                "created_date": "2026-02-24T16:36:58+00:00",
                "responsible_org_id": "a4133505-eb55-42d6-9c54-582dd21c7014",
                "responsible_org_name": "Open Data Services",
                "user_application_id": "cb8e551b-c1d5-46bc-a769-5c1ea38caad3",
                "user_application_name": "IATI Account",
                "user_name": "SK Test08",
                "user_id": "560e0f39-829a-6d50-7505-69490018773f",
            }
        ],
        "message_type": "DATASET_DELETED",
        "message_date": "2026-02-24T16:36:58+00:00",
    }

    message_processor.dispatch_event("DATASET_DELETED", message_payload)

    assert models.Dataset.objects.count() == 0
