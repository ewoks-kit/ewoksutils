import gc
import logging
from logging.handlers import QueueHandler
from queue import Queue

from .. import sqlite3_utils
from ..logging_utils.asyncwrapper import AsyncHandlerWrapper
from ..logging_utils.cleanup import cleanup_logger
from ..logging_utils.connection import ConnectionHandler
from ..logging_utils.sqlite3 import Sqlite3Handler


def test_cleanup_logger():
    logger = logging.getLogger(__name__)
    q = Queue()
    h = QueueHandler(q)
    logger.addHandler(h)
    logger.setLevel(logging.INFO)
    h.setLevel(logging.INFO)

    logger.info("info message 1")
    assert q.qsize() == 1

    cleanup_logger(__name__)
    assert q.qsize() == 0


def test_connection_handler():
    connected = None
    destination = list()
    expected = list()

    class Connection:
        def __init__(self):
            nonlocal connected
            connected = True

        def __del__(self):
            nonlocal connected
            connected = False

    class MyHandler(ConnectionHandler):
        def _connect(self, timeout=1) -> None:
            self._connection = Connection()

        def _disconnect(self) -> None:
            del self._connection
            self._connection = None

        def _send_serialized_record(self, srecord):
            destination.append(srecord)

        def _serialize_record(self, record):
            msg = self.format(record)
            return record.levelno, msg

    logger = logging.getLogger(__name__)

    logger.setLevel(logging.INFO)
    handler = MyHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Check lazy connecting
    assert not connected
    assert destination == expected

    logger.debug("debug message")
    assert not connected
    assert destination == expected

    logger.info("info message 1")
    expected.append((logging.INFO, "info message 1"))
    assert connected
    assert destination == expected

    # Check closing a handler
    handler.close()
    assert not connected

    # Check reconnect
    logger.info("info message 2")
    expected.append((logging.INFO, "info message 2"))
    assert connected
    assert destination == expected

    # Check connection closed when no reference to the handler anymore
    logger.removeHandler(handler)
    handler = None
    while gc.collect():
        pass
    assert not connected

    handler = MyHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("info message 3")
    expected.append((logging.INFO, "info message 3"))
    assert connected
    assert destination == expected

    # Check connection closed when no reference to the logger anymore
    handler = None
    logger = None
    cleanup_logger(__name__)
    while gc.collect():
        pass
    assert not connected


def test_sqlite3_handler(tmp_path):
    logger = logging.getLogger(__name__)
    uri = str(tmp_path / "subdir" / "test.db")
    field_types = {"field1": 0, "field2": "", "field3": True, "field4": 0.0}
    handler = Sqlite3Handler(uri, "mytable", field_types)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    handler.setLevel(logging.INFO)

    expected = list()
    logger.info("message1")
    expected.append({"field1": None, "field2": None, "field3": None, "field4": None})
    logger.info("message2", extra={"field2": "2"})
    expected.append({"field1": None, "field2": "2", "field3": None, "field4": None})
    logger.info(
        "message2", extra={"field1": 1, "field2": "2", "field3": True, "field4": 1.1}
    )
    expected.append({"field1": 1, "field2": "2", "field3": True, "field4": 1.1})

    with sqlite3_utils.connect(uri, uri=True, check_same_thread=False) as conn:
        rows = list(sqlite3_utils.select(conn, "mytable", field_types=field_types))

    assert rows == expected

    types = {"field1": int, "field2": str, "field3": bool, "field4": float}
    for row in rows:
        for name, value in row.items():
            if value is not None:
                vtype = types[name]
                assert isinstance(value, vtype), name

    cleanup_logger(__name__)


def test_async_wrapper():
    logger = logging.getLogger(__name__)
    q = Queue()
    h = AsyncHandlerWrapper(QueueHandler(q))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)
    h.setLevel(logging.INFO)

    logger.info("message")
    assert q.get(timeout=3).msg == "message"

    cleanup_logger(__name__)
