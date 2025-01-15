"""
WSGI config for IATI Dashboard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

# Import data here so it's in gunicorn's preload
import data  # noqa F401
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ui.settings")

application = get_wsgi_application()
