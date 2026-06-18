import asyncio
import json
import traceback
from datetime import datetime, timezone

import sentry_sdk
from asgiref.sync import sync_to_async
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.exceptions import ServiceBusConnectionError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import DateTimeField, Q, TextField
from django.db.models.functions import Cast
from django.db.utils import IntegrityError

from ..models import Dataset, DatasetEvent, DatasetEventTypes, ReportingOrg
from .message_processor_error import MessageProcessorRuntimeError
from .utilities import get_datetime_with_tz


class MessageProcessor:

    def __init__(self, args):
        self._service_loop_sleep = args["REALTIME_UPDATE_SERVICE_LOOP_SLEEP"]
        self._service_loop_sleep_after_error = args["REALTIME_UPDATE_SERVICE_LOOP_SLEEP_AFTER_ERROR"]
        self._connection_str = args["AZ_SERVICE_BUS_CONNECTION_STRING"]
        self._topics_and_subs = [
            (
                args["AZ_SERVICE_BUS_REGISTRY_CHANGES_TOPIC_NAME"],
                args["AZ_SERVICE_BUS_REGISTRY_CHANGES_SUBSCRIPTION_NAME"],
            ),
            (
                args["AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_TOPIC_NAME"],
                args["AZ_SERVICE_BUS_DATASET_CHECK_RESULTS_SUBSCRIPTION_NAME"],
            ),
        ]
        self._stop_event = asyncio.Event()
        self._sb_client = None

    def run(self):
        try:
            asyncio.run(self.service_loop())
        except KeyboardInterrupt:
            print("\n")
            print("User pressed Ctrl-C. Exiting")

    async def service_loop(self):
        self._sb_client = ServiceBusClient.from_connection_string(conn_str=self._connection_str, logging_enable=True)
        try:
            while True:
                await self.fetch_and_process_messages()
                await asyncio.sleep(self._service_loop_sleep)
        finally:
            await self._sb_client.close()

    async def fetch_and_process_messages(self):
        try:
            for topic, sub in self._topics_and_subs:
                self.print_with_timestamp(f"Checking {sub} for messages")
                receiver = self._sb_client.get_subscription_receiver(topic, sub, max_wait_time=1)
                async with receiver:
                    received_msgs = await receiver.receive_messages(max_wait_time=1, max_message_count=250)
                    for msg in received_msgs:
                        if not msg.application_properties:
                            self.print_with_timestamp(
                                f"MessageProcessor.fetch_and_process_messages - skipping msg because it has no application_properties"
                            )
                            await receiver.complete_message(msg)
                            continue
                        try:
                            await sync_to_async(self.dispatch_event, thread_sensitive=True)(
                                msg.application_properties[b"message_type"].decode("utf-8"), json.loads(str(msg))
                            )
                        except MessageProcessorRuntimeError as e:
                            self.print_with_timestamp(e)
                        await receiver.complete_message(msg)
        except ServiceBusConnectionError as e:
            self.print_with_timestamp(
                f"MessageProcessor.fetch_and_process_messages - Could not connect to Azure Service Bus, trying again in 15s - {e}"
            )
            await asyncio.sleep(self._service_loop_sleep_after_error)
        except Exception as e:
            self.print_with_timestamp(f"MessageProcessor.fetch_and_process_messages - Unexpected Error - {e}")
            print(traceback.format_exc())
            sentry_sdk.capture_exception(e)

    def dispatch_event(self, message_type: str, message_payload: dict):
        try:
            match message_type:
                case "DATASET_CREATED":
                    self.process_registry_dataset_created(message_payload)
                case "DATASET_UPDATED":
                    self.process_registry_dataset_updated(message_payload)
                case "REPORTING_ORG_CREATED":
                    self.process_registry_reporting_org_created(message_payload)
                case "REPORTING_ORG_UPDATED":
                    self.process_registry_reporting_org_updated(message_payload)
                case "DATASET_DELETED" | "REPORTING_ORG_DELETED":
                    record_type = "dataset" if message_type == "DATASET_DELETED" else "reporting_org"
                    self.process_registry_record_deleted(record_type, message_payload)
                case "DATASET_CHECK_RESULT":
                    self.process_bulk_data_service_dataset_check_result(message_payload)
                case _:
                    print("Received unknown message type: ")
                    print(json.dumps(message_payload))
        except KeyError as e:
            raise MessageProcessorRuntimeError(
                f"MessageProcessor.dispatch_event - ERROR - KeyError ({e}) handling message of type {message_type}. "
                f"Received message likely not in correct format. {traceback.format_exc()}"
            )

    def process_bulk_data_service_dataset_check_result(self, message_payload: dict):

        dataset_check_result_current = message_payload["dataset_check_result_current"]
        dataset_check_result_previous = message_payload.get("dataset_check_result_previous", None)

        self.update_most_recent_dataset_check_field(dataset_check_result_current)

        if (dataset_check_result_previous is not None) and (
            dataset_check_result_current.get("last_known_good_dataset", {}).get("hash", "")
            != dataset_check_result_previous.get("last_known_good_dataset", {}).get("hash", "")
            or dataset_check_result_current["most_recent_get_attempt"]["error_occurred"]
            != dataset_check_result_previous["most_recent_get_attempt"]["error_occurred"]
            or dataset_check_result_current["most_recent_get_attempt"]["http_status"]
            != dataset_check_result_previous["most_recent_get_attempt"]["http_status"]
        ):
            self.save_dataset_check_result_change_event(message_payload)
            self.print_with_timestamp(
                f"dataset id: {dataset_check_result_current["id"]} - Saved new DatasetEvent as hash or download "
                "status has changed"
            )

    def save_dataset_check_result_change_event(self, message_payload: dict):
        dataset_event = DatasetEvent()
        dataset_event.timestamp = get_datetime_with_tz(message_payload["message_date"])
        dataset_event.dataset_id = message_payload["dataset_check_result_current"]["id"]
        dataset_event.reporting_org_id = message_payload["dataset_check_result_current"]["id"]
        dataset_event.initiating_user_id = None
        dataset_event.initiating_user_name = None
        dataset_event.initiating_organisation_id = None
        dataset_event.initiating_organisation_name = None
        dataset_event.initiating_application_id = "5bb64df4-84e1-4d44-8071-e1c396ba950a"
        dataset_event.initiating_application_name = "Bulk Data Service"
        dataset_event.event_type = DatasetEventTypes.DATASET_DOWNLOAD_STATUS_CHANGED
        dataset_event.message_payload = message_payload
        dataset_event.data_fields_current = message_payload["dataset_check_result_current"]
        dataset_event.data_fields_previous = message_payload["dataset_check_result_previous"]
        dataset_event.save()

    def update_most_recent_dataset_check_field(self, dataset_check_result: dict):
        if Dataset.objects.filter(pk=dataset_check_result["id"]).exists():

            q = Dataset.objects.annotate(
                _=Cast("most_recent_dataset_check_result__last_update_check", TextField())
            ).annotate(last_update_check=Cast("_", DateTimeField()))

            num_matched = q.filter(
                Q(pk=dataset_check_result["id"]),
                Q(last_update_check__isnull=True)
                | Q(last_update_check__lte=get_datetime_with_tz(dataset_check_result["last_update_check"])),
            ).update(most_recent_dataset_check_result=dataset_check_result)

            if num_matched == 1:
                self.print_with_timestamp(
                    f"dataset id: {dataset_check_result["id"]} - Updated record with new dataset check result"
                )
            else:
                self.print_with_timestamp(
                    f"dataset id: {dataset_check_result["id"]} - Skipped updating record with dataset check "
                    "because the dataset check result's 'last_update_check' field is not newer than existing record"
                )

        else:
            self.print_with_timestamp(
                f"dataset id: {dataset_check_result["id"]} - Failed to update with new dataset check result "
                "because dataset does not exist in the database."
            )

    def process_registry_dataset_created(self, message_payload: dict):
        try:
            dataset = Dataset(
                id=message_payload["dataset"]["id"],
                short_name=message_payload["dataset"]["short_name"],
                source_url=message_payload["dataset"]["url"],
                reporting_org=ReportingOrg.objects.get(id=message_payload["dataset"]["reporting_org_id"]),
            )
            dataset.save()
            self.print_success("created", "dataset", message_payload["dataset"])
        except ReportingOrg.DoesNotExist:
            self.print_with_timestamp(
                f"Failed to create dataset with ID {message_payload["dataset"]["id"]} because "
                f"the parent reporting_org is not in the database"
            )
        except IntegrityError as e:
            self.print_with_timestamp(
                f"Failed to create dataset with ID {message_payload["dataset"]["id"]} because {str(e).replace('\n', ', ')}"
            )

    def process_registry_reporting_org_created(self, message_payload: dict):
        try:
            reporting_org = ReportingOrg(
                id=message_payload["reporting_org"]["id"],
                short_name=message_payload["reporting_org"]["short_name"],
                human_readable_name=message_payload["reporting_org"]["human_readable_name"],
            )
            reporting_org.save()
            self.print_success("created", "reporting_org", message_payload["reporting_org"])
        except IntegrityError as e:
            self.print_with_timestamp(
                f"Failed to create dataset with ID {message_payload["reporting_org"]["id"]} because {str(e).replace('\n', ', ')}"
            )

    def process_registry_dataset_updated(self, message_payload: dict):
        try:
            dataset = Dataset.objects.get(id=message_payload["dataset"]["id"])
            dataset.short_name = message_payload["dataset"]["short_name"]
            dataset.source_url = message_payload["dataset"]["url"]
            dataset.reporting_org = ReportingOrg.objects.get(id=message_payload["dataset"]["reporting_org_id"])
            dataset.save()
            self.print_success("updated", "dataset", message_payload["dataset"])
        except ReportingOrg.DoesNotExist:
            self.print_with_timestamp(
                f"Failed to update dataset with ID {message_payload["dataset"]["id"]} because "
                f"the new parent reporting_org is not in the database"
            )
        except Dataset.DoesNotExist:
            self.print_with_timestamp(
                f"Failed to update dataset with ID {message_payload["dataset"]["id"]} because "
                f"the dataset is not in the database"
            )
        except IntegrityError:
            self.print_with_timestamp(
                f"Failed to update dataset with ID {message_payload["dataset"]["id"]} because "
                f"the new short_name is already in use"
            )

    def process_registry_reporting_org_updated(self, message_payload: dict):
        try:
            reporting_org = ReportingOrg.objects.get(id=message_payload["reporting_org"]["id"])
            reporting_org.short_name = message_payload["reporting_org"]["short_name"]
            reporting_org.human_readable_name = message_payload["reporting_org"]["human_readable_name"]
            reporting_org.save()
            self.print_success("updated", "reporting_org", message_payload["reporting_org"])
        except ReportingOrg.DoesNotExist:
            self.print_with_timestamp(
                f"Failed to update reporting_org with ID {message_payload["reporting_org"]["id"]} because "
                f"the reporting_org is not in the database"
            )
        except IntegrityError:
            self.print_with_timestamp(
                f"Failed to update reporting_org with ID {message_payload["reporting_org"]["id"]} because "
                f"the new short_name is already in use"
            )

    def process_registry_record_deleted(self, record_type: str, message_payload: dict):
        Model = Dataset if record_type == "dataset" else ReportingOrg
        try:
            record = Model.objects.get(id=message_payload[record_type]["id"])
            record.delete()
            self.print_success("deleted", record_type, message_payload[record_type])
        except ObjectDoesNotExist:
            self.print_with_timestamp(
                f"Failed to delete {record_type} with ID {message_payload[record_type]["id"]} because "
                f"the {record_type} is not in the database"
            )

    def print_success(self, change: str, record_type: str, record: dict):
        self.print_with_timestamp(f"{change.capitalize()} {record_type} with ID {record["id"]}")

    def print_with_timestamp(self, s: str):
        print(f"{datetime.now(timezone.utc).isoformat()} - {s}")
