from django.core.management.base import BaseCommand

from iati_dashboard.make_plots import make_plots


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--verbose", action="store_true", help="Output verbose progress to stdout")

    def handle(self, *args, **options):
        make_plots(options.get("verbose", False))
