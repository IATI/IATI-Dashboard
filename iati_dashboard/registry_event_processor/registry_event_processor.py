import asyncio
import json
import traceback
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus.exceptions import ServiceBusConnectionError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from ..models import Dataset, ReportingOrg


class RegistryEventProcessor:

    def __init__(self, args):
        self._connection_str = args["AZ_SERVICE_BUS_CONNECTION_STRING"]
        self._topic_name = args["AZ_SERVICE_BUS_TOPIC_NAME"]
        self._subscription_name = args["AZ_SERVICE_BUS_SUBSCRIPTION_NAME"]
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
                await asyncio.sleep(3)
        finally:
            await self._sb_client.close()

    async def fetch_and_process_messages(self):
        self.print_with_timestamp("Checking for messages")
        try:
            receiver = self._sb_client.get_subscription_receiver(
                topic_name=self._topic_name, subscription_name=self._subscription_name, max_wait_time=1
            )
            async with receiver:
                received_msgs = await receiver.receive_messages(max_wait_time=1, max_message_count=5)
                for msg in received_msgs:
                    await sync_to_async(self.dispatch_registry_event, thread_sensitive=True)(
                        msg.application_properties[b"message_type"].decode("utf-8"), json.loads(str(msg))
                    )
                    await receiver.complete_message(msg)
        except ServiceBusConnectionError as e:
            self.print_with_timestamp(
                f"RegistryEventProcessor.fetch_and_process_messages - Could not connect to Azure Service Bus, trying again in 15s - {e}"
            )
            await asyncio.sleep(15)
        except Exception as e:
            self.print_with_timestamp(f"RegistryEventProcessor.fetch_and_process_messages - Unexpected Error - {e}")
            print(traceback.format_exc())

    def dispatch_registry_event(self, message_type: str, message_payload: dict):
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
            case _:
                print("Received unknown message type: ")
                print(json.dumps(message_payload))

    def process_registry_dataset_created(self, message_payload: dict):
        try:
            dataset = Dataset(
                id=message_payload["dataset"]["id"],
                short_name=message_payload["dataset"]["short_name"],
                source_url=message_payload["dataset"]["url"],
                stats_json={},
                reporting_org=ReportingOrg.objects.get(id=message_payload["dataset"]["reporting_org_id"]),
                registry_metadata_realtime=message_payload["dataset"],
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
                stats_json={"activity_files": 0, "organisation_files": 0},
                registry_metadata_realtime=message_payload["reporting_org"],
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
            dataset.registry_metadata_realtime = message_payload["dataset"]
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
            reporting_org.registry_metadata_realtime = message_payload["reporting_org"]
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
