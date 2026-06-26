import datetime
import importlib
import uuid
from pathlib import Path

from django.db import connections
from django.test import TestCase
from django.urls import reverse

import iati_dashboard.data
from iati_dashboard import models

DATASET_ACTIVITY_STREAM_SQL = Path(__file__).resolve().parent.parent / "tests" / "sql" / "dataset_activity_stream.sql"


def _create_dataset_activity_stream_table() -> None:
    """Create the dataset_activity_stream table in the activity_stream test DB.

    The DatasetHistoricEvent model is managed=False (becaause the DB table is
    managed via the iati-activity-stream app), so Django's test runner will not
    auto-create the table. Run the schema SQL once per test class.
    """
    with connections["activity_stream"].cursor() as cursor:
        cursor.execute(DATASET_ACTIVITY_STREAM_SQL.read_text())


class BasicPageTests(TestCase):
    """Perform basic HTTP 200/404 checks on the Dashboard pages

    These are split up into a number of functions because some can
    take some time to run and so running with the "-v 2" flag will
    list the tests as they run.
    """

    databases = {"default", "activity_stream"}
    fixtures = ["reporting_orgs", "datasets"]

    @classmethod
    def setUpClass(cls) -> None:
        # We need to do this because data.py imports the stats JSON at import time
        importlib.reload(iati_dashboard.data)
        super().setUpClass()
        _create_dataset_activity_stream_table()

    def test_top_pages(self):
        """Test the index and top hierarchy pages return a 200 status code"""

        self.assertEqual(self.client.get(reverse("dash-index")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-headlines-publishers")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-headlines-publisher-detail", args=("zsl",))).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("dash-headlines-dataset-detail", args=("zsl-activity",))).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("dash-headlines-publisher-detail", args=("not-a-valid-publisher",))).status_code,
            404,
        )
        self.assertEqual(self.client.get(reverse("dash-errors")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-publishingstats")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-exploringdata")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-faq")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-registrationagencies")).status_code, 200)

    def test_errors(self):
        """Test the data quality pages"""

        self.assertEqual(self.client.get(reverse("dash-errors-download")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-errors-xml")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-errors-validation")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-identifiers")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-errors-reportingorgs")).status_code, 200)

    def test_publishingstats_timeliness(self):
        """Test timeliness pages in the publishing statistics section"""

        self.assertEqual(self.client.get(reverse("dash-publishingstats-timeliness-frequency")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-publishingstats-timeliness-timelag")).status_code, 200)

    def test_publishingstats_comprehensiveness(self):
        """Test comprehensiveness pages in the publishing statistics section"""

        self.assertEqual(self.client.get(reverse("dash-publishingstats-comprehensiveness-summary")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-publishingstats-comprehensiveness-core")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("dash-publishingstats-comprehensiveness-financials")).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("dash-publishingstats-comprehensiveness-valueadded")).status_code, 200
        )

    def test_publishingstats_forwardlooking(self):
        """Test the forward looking page in the publishing statistics section"""

        self.assertEqual(self.client.get(reverse("dash-publishingstats-forwardlooking")).status_code, 200)

    def test_publishingstats_summarystats(self):
        """Test the summary statistics page in the publishing statistics section"""

        self.assertEqual(self.client.get(reverse("dash-publishingstats-summarystats")).status_code, 200)

    def test_publishingstats_humanitarian(self):
        """Test the humanitarian page in the publishing statistics section"""

        self.assertEqual(self.client.get(reverse("dash-publishingstats-humanitarian")).status_code, 200)

    def test_exploringdata(self):
        """Test the exploring data pages"""
        self.assertEqual(self.client.get(reverse("dash-headlines-files")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-headlines-activities")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-exploringdata-booleans")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-exploringdata-codelists")).status_code, 200)
        self.assertEqual(
            self.client.get(
                reverse(
                    "dash-exploringdata-codelists-detail",
                    args=(
                        "2",
                        "budget_@type",
                    ),
                )
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    "dash-exploringdata-codelists-detail",
                    args=(
                        "2",
                        "not-a-valid-slug",
                    ),
                )
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    "dash-exploringdata-codelists-detail",
                    args=(
                        "3",
                        "budget_@type",
                    ),
                )
            ).status_code,
            404,
        )
        self.assertEqual(self.client.get(reverse("dash-exploringdata-dates")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-versions")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-organisation")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-licenses")).status_code, 200)
        self.assertEqual(self.client.get(reverse("dash-licenses-detail", args=("cc-by",))).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("dash-licenses-detail", args=("not-a-valid-license",))).status_code,
            404,
        )
        self.assertEqual(self.client.get(reverse("dash-exploringdata-elements")).status_code, 200)
        self.assertEqual(
            self.client.get(
                reverse("dash-exploringdata-elements-detail", args=("iati-activity_activity-date_@iso-date",))
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("dash-exploringdata-elements-detail", args=("not-a-valid-element",))).status_code,
            404,
        )
        self.assertEqual(self.client.get(reverse("dash-exploringdata-orgids")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("dash-exploringdata-orgtypes-detail", args=("funding_org",))).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("dash-exploringdata-orgtypes-detail", args=("not-a-valid-org-type",))).status_code,
            404,
        )
        self.assertEqual(self.client.get(reverse("dash-exploringdata-traceability")).status_code, 200)


class DatasetHistoryPaginationTests(TestCase):
    """Page-number pagination checks for the per-dataset History section."""

    databases = {"default", "activity_stream"}
    fixtures = ["reporting_orgs", "datasets"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        _create_dataset_activity_stream_table()

    def setUp(self) -> None:
        self.dataset = models.Dataset.objects.get(short_name="zsl-activity")
        with connections["activity_stream"].cursor() as cursor:
            cursor.execute("DELETE FROM dataset_activity_stream WHERE dataset_id = %s", [str(self.dataset.id)])

    def _insert_events(self, count: int, base_time: datetime.datetime) -> None:
        for i in range(count):
            models.DatasetHistoricEvent.objects.using("activity_stream").create(
                id=uuid.uuid4(),
                message_type="DATASET_UPDATED",
                message_date=base_time + datetime.timedelta(seconds=i),
                dataset_id=self.dataset.id,
                payload={},
            )

    def test_pagination(self) -> None:
        base_time = datetime.datetime(2026, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
        self._insert_events(60, base_time)
        url = reverse("dash-headlines-dataset-detail", args=(self.dataset.short_name,))

        page1 = self.client.get(url)
        self.assertEqual(page1.status_code, 200)
        page1_body = page1.content.decode("utf-8")
        self.assertEqual(page1_body.count('class="history-entry"'), 25)
        self.assertIn("?page=2", page1_body)
        self.assertNotIn("?page=1", page1_body)

        page2 = self.client.get(url + "?page=2")
        self.assertEqual(page2.status_code, 200)
        page2_body = page2.content.decode("utf-8")
        self.assertEqual(page2_body.count('class="history-entry"'), 25)
        self.assertIn("?page=1", page2_body)
        self.assertIn("?page=3", page2_body)

        page3 = self.client.get(url + "?page=3")
        self.assertEqual(page3.status_code, 200)
        page3_body = page3.content.decode("utf-8")
        self.assertEqual(page3_body.count('class="history-entry"'), 10)
        self.assertIn("?page=2", page3_body)
        self.assertNotIn("?page=4", page3_body)

    def test_empty_history(self) -> None:
        url = reverse("dash-headlines-dataset-detail", args=(self.dataset.short_name,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.content.decode("utf-8")
        self.assertIn('id="h_history"', body)
        self.assertIn("No history yet for this dataset.", body)
        self.assertNotIn("?page=", body)


class OriginalDashboardRedirectTests(TestCase):
    """Perform basic HTTP 301 redirection checks on the Dashboard pages

    These are split up into a number of functions because some can
    take some time to run and so running with the "-v 2" flag will
    list the tests as they run.
    """

    fixtures = ["reporting_orgs"]

    def _url_and_view_helper(self, urls_and_views_to_check):
        """Checks that a set of URLs redirect to matching view functions"""

        for url, view_name in urls_and_views_to_check.items():
            self.assertRedirects(self.client.get(f"/{url}.html"), reverse(view_name), status_code=301)

    def test_headlines_and_misc(self):
        """Test headlines and miscellaneous pages redirect to their new locations"""

        # This is not particularly DRY as a similar dictionary is created in views.py
        # but I think this is minor as that may disappear from views.py in a future
        # refactor of what goes into the context.
        self._url_and_view_helper(
            {
                "index": "dash-index",
                "headlines": "dash-index",
                "files": "dash-headlines-files",
                "activities": "dash-headlines-activities",
                "publishers": "dash-headlines-publishers",
                "faq": "dash-faq",
                "registration_agencies": "dash-registrationagencies",
            }
        )

    def test_errors(self):
        """Test data quality pages redirect to their new locations"""

        # This is not particularly DRY as a similar dictionary is created in views.py
        # but I think this is minor as that may disappear from views.py in a future
        # refactor of what goes into the context.
        self._url_and_view_helper(
            {
                "data_quality": "dash-errors",
                "download": "dash-errors-download",
                "xml": "dash-errors-xml",
                "validation": "dash-errors-validation",
                "versions": "dash-versions",
                "organisation": "dash-organisation",
                "identifiers": "dash-identifiers",
                "reporting_orgs": "dash-errors-reportingorgs",
                "licenses": "dash-licenses",
            }
        )

    def test_publishingstats(self):
        """Test publishing stats pages redirect to their new locations"""

        # This is not particularly DRY as a similar dictionary is created in views.py
        # but I think this is minor as that may disappear from views.py in a future
        # refactor of what goes into the context.
        self._url_and_view_helper(
            {
                "publishing_stats": "dash-publishingstats",
                "timeliness": "dash-publishingstats-timeliness-frequency",
                "timeliness_timelag": "dash-publishingstats-timeliness-timelag",
                "forwardlooking": "dash-publishingstats-forwardlooking",
                "comprehensiveness": "dash-publishingstats-comprehensiveness-summary",
                "comprehensiveness_core": "dash-publishingstats-comprehensiveness-core",
                "comprehensiveness_financials": "dash-publishingstats-comprehensiveness-financials",
                "comprehensiveness_valueadded": "dash-publishingstats-comprehensiveness-valueadded",
                "summary_stats": "dash-publishingstats-summarystats",
                "humanitarian": "dash-publishingstats-humanitarian",
            }
        )

    def test_exploringdata(self):
        """Test exploring data pages redirect to their new locations"""

        # This is not particularly DRY as a similar dictionary is created in views.py
        # but I think this is minor as that may disappear from views.py in a future
        # refactor of what goes into the context.
        self._url_and_view_helper(
            {
                "exploring_data": "dash-exploringdata-elements",
                "elements": "dash-exploringdata-elements",
                "codelists": "dash-exploringdata-codelists",
                "booleans": "dash-exploringdata-booleans",
                "dates": "dash-exploringdata-dates",
                "traceability": "dash-exploringdata-traceability",
                "org_ids": "dash-exploringdata-orgids",
            }
        )

    def test_slug_page_redirects(self):
        """Test pages with slugs redirect to their new locations"""

        self.assertRedirects(
            self.client.get(r"/publisher/zsl.html"),
            reverse("dash-headlines-publisher-detail", args=["zsl"]),
            status_code=301,
        )
        self.assertRedirects(
            self.client.get(r"/license/cc-by.html"), reverse("dash-licenses-detail", args=["cc-by"]), status_code=301
        )
        self.assertRedirects(
            self.client.get(r"/codelist/2/budget_@type.html"),
            reverse("dash-exploringdata-codelists-detail", args=["2", "budget_@type"]),
            status_code=301,
        )
        self.assertRedirects(
            self.client.get(r"/element/iati-activity_activity-date_@iso-date.html"),
            reverse("dash-exploringdata-elements-detail", args=["iati-activity_activity-date_@iso-date"]),
            status_code=301,
        )
        self.assertRedirects(
            self.client.get(r"/org_type/funding_org.html"),
            reverse("dash-exploringdata-orgtypes-detail", args=["funding_org"]),
            status_code=301,
        )
