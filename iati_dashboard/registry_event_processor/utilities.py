import datetime


def get_datetime_with_tz(isodate: str = "") -> datetime.datetime:
    if isodate == "":
        return datetime.datetime.now(tz=datetime.timezone.utc).replace(microsecond=0)
    else:
        return datetime.datetime.fromisoformat(isodate).replace(microsecond=0)
