"""
WSGI config for IATI Dashboard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iati_dashboard.settings")

application = get_wsgi_application()

# Import and run a view here, so that gunicorn's preload will include these
# (running a view effectively caches some data for future view runs)
import iati_dashboard.data  # noqa F401, F402
from iati_dashboard.ui.views import index  # noqa F402

index(None)
