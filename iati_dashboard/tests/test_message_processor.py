import datetime
import pytest

from iati_dashboard import models
from iati_dashboard.realtime_message_processor.message_processor import MessageProcessor


@pytest.mark.django_db
def test_datasets_created():
    reporting_org = models.ReportingOrg(id="a4133505-eb55-42d6-9c54-582dd21c7014", short_name="odsc")
    reporting_org.save()

    message_processor = MessageProcessor(
        {
            "REALTIME_UPDATE_SERVICE_LOOP_SLEEP": None,
            "REALTIME_UPDATE_SERVICE_LOOP_SLEEP_AFTER_ERROR": None,
            "AZ_SERVICE_BUS_CONNECTION_STRING": None,
            "AZ_SERVICE_BUS_REGISTRY_CHANGES_TOPIC_NAME": None,
            "AZ_SERVICE_BUS_REGISTRY_CHANGES_SUBSCRIPTION_NAME": None,
            "AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_TOPIC_NAME": None,
            "AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_SUBSCRIPTION_NAME": None,
        }
    )
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
    message_processor.process_registry_dataset_created(message_payload)

    dataset = models.Dataset.objects.get(short_name="ods-sample-2")

    assert dataset.metadata_json_datetime == datetime.datetime(2026, 2, 24, 16, 30, 4, tzinfo=datetime.timezone.utc)

    assert "activities" in dataset.stats_json
    assert "organisations" in dataset.stats_json
    assert "activity_files" in dataset.stats_json
    assert "organisation_files" in dataset.stats_json
    assert "file_size" in dataset.stats_json
    assert "hierarchies" in dataset.stats_json
    assert "reporting_orgs" in dataset.stats_json


@pytest.mark.django_db
def test_datasets_deleted():
    reporting_org = models.ReportingOrg(id="a4133505-eb55-42d6-9c54-582dd21c7014", short_name="odsc")
    reporting_org.save()

    dataset = models.Dataset(
        id="4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8", short_name="ods-sample-2", reporting_org=reporting_org
    )
    dataset.save()

    message_processor = MessageProcessor(
        {
            "REALTIME_UPDATE_SERVICE_LOOP_SLEEP": None,
            "REALTIME_UPDATE_SERVICE_LOOP_SLEEP_AFTER_ERROR": None,
            "AZ_SERVICE_BUS_CONNECTION_STRING": None,
            "AZ_SERVICE_BUS_REGISTRY_CHANGES_TOPIC_NAME": None,
            "AZ_SERVICE_BUS_REGISTRY_CHANGES_SUBSCRIPTION_NAME": None,
            "AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_TOPIC_NAME": None,
            "AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_SUBSCRIPTION_NAME": None,
        }
    )
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

    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(short_name="ods-sample-2")
    with pytest.raises(models.Dataset.DoesNotExist):
        models.Dataset.objects.get(id="4cbb8654-4446-f3e5-e7dd-699dd2c3a3c8")
