import json
import os

import django.core.exceptions
from django.conf import settings

os.makedirs("cache", exist_ok=True)


# JSON cache for a function with no arguments
def json_cache(fname):
    fname = os.path.join("cache", fname)

    def decorator(f):
        def wrapper():
            # Check in memory cache first
            if hasattr(f, "__cache"):
                return f.__cache
            is_json_file = os.path.isfile(fname)
            if is_json_file:
                with open(fname) as fp:
                    try:
                        res = json.load(fp)
                    except json.decoder.JSONDecodeError:
                        is_json_file = False
            if not is_json_file:
                res = list(f())
                try:
                    if settings.DASHBOARD_CREATE_CACHE_FILES:
                        with open(fname, "w") as fp:
                            json.dump(res, fp)
                except django.core.exceptions.ImproperlyConfigured:
                    pass
            f.__cache = res
            return res

        return wrapper

    return decorator
