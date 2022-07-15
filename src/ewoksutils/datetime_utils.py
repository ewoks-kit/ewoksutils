from datetime import datetime


def fromisoformat(s: str) -> datetime:
    if hasattr(datetime, "fromisoformat"):
        return datetime.fromisoformat(s)
    else:
        # python < 3.7
        try:
            return datetime.strptime(s[:-3] + s[-2:], "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            pass
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
