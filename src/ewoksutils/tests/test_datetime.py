from datetime import datetime

from ..datetime_utils import fromisoformat


def test_isoformat_without_timezone():
    dt = datetime.now()
    assert fromisoformat(dt.isoformat()) == dt


def test_isoformat_with_timezone():
    dt = datetime.now().astimezone()
    assert fromisoformat(dt.isoformat()) == dt
