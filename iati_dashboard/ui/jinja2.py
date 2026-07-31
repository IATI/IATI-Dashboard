"""Jinja2 template configuration"""

import re

from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html

from jinja2 import Environment

from .. import timeliness


def round_nicely(val, ndigits=0):
    """Round a float, but remove the trailing .0 from integers that python insists on"""
    if val == "-":
        return val
    val = round(float(val), ndigits)
    if val == int(val):
        return int(val)


def xpath_to_url(path):
    path = path.strip("./")
    # remove conditions
    path = re.sub(r"\[[^]]+\]", "", path)
    if path.startswith("iati-activity"):
        url = "https://iatistandard.org/activity-standard/iati-activities/" + path.split("@")[0]
    elif path.startswith("iati-organisation"):
        url = "https://iatistandard.org/organisation-standard/iati-organisations/" + path.split("@")[0]
    else:
        url = "https://iatistandard.org/activity-standard/iati-activities/iati-activity/" + path.split("@")[0]
    if "@" in path:
        url += "#attributes"
    return url


def linkurl(url, link_text=None):
    if url.startswith("https://") or url.startswith("https://"):
        return format_html('<a href="{}" rel="noopener">{}</a>', url, link_text or url)
    else:
        return link_text or url


def sum_all_dict_values_except_key(a_dict, except_key):
    return sum(value for (key, value) in a_dict.items() if key != except_key)


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
        }
    )
    env.filters["url_to_filename"] = lambda x: x.rstrip("/").split("/")[-1]
    env.filters["has_future_transactions"] = timeliness.has_future_transactions
    env.filters["xpath_to_url"] = xpath_to_url
    env.filters["round_nicely"] = round_nicely
    env.filters["linkurl"] = linkurl
    env.filters["sum_all_dict_values_except_key"] = sum_all_dict_values_except_key
    return env
