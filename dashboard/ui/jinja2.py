"""Jinja2 template configuration
"""
import re

from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment
import timeliness


def round_nicely(val, ndigits=2):
    """ Round a float, but remove the trailing .0 from integers that python insists on
    """
    if int(val) == float(val):
        return int(val)
    return round(float(val), ndigits)


def xpath_to_url(path):
    path = path.strip('./')
    # remove conditions
    path = re.sub(r'\[[^]]+\]', '', path)
    if path.startswith('iati-activity'):
        url = 'http://iatistandard.org/activity-standard/iati-activities/' + path.split('@')[0]
    elif path.startswith('iati-organisation'):
        url = 'http://iatistandard.org/organisation-standard/iati-organisations/' + path.split('@')[0]
    else:
        url = 'http://iatistandard.org/activity-standard/iati-activities/iati-activity/' + path.split('@')[0]
    if '@' in path:
        url += '#attributes'
    return url


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            'static': static,
            'url': reverse,
        }
    )
    env.filters['url_to_filename'] = lambda x: x.rstrip('/').split('/')[-1]
    env.filters['has_future_transactions'] = timeliness.has_future_transactions
    env.filters['xpath_to_url'] = xpath_to_url
    env.filters['round_nicely'] = round_nicely
    return env
