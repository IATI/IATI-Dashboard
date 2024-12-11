from django.conf import settings

import comprehensiveness
import forwardlooking
import humanitarian
import summary_stats
import timeliness

settings.configure(DASHBOARD_CREATE_CACHE_FILES=True)

timeliness.publisher_frequency()
timeliness.publisher_timelag()
forwardlooking.table()
comprehensiveness.table()
summary_stats.table()
humanitarian.table()
