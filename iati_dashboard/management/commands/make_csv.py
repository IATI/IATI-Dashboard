from django.core.management.base import BaseCommand

from iati_dashboard.make_csv import make_csv


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--verbose", action="store_true", help="Output progress to stdout")

    def handle(self, *args, **options):
        make_csv(options.get("verbose", False))
