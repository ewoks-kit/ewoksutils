import logging
import sqlite3
import threading
import time
from typing import Optional

from .. import sqlite3_utils
from ..logging_utils.sqlite3 import Sqlite3Handler

FIELD_TYPES = {"field1": 0, "field2": ""}


def _sqlite3_retry_period() -> Optional[float]:
    """Sqlite3Handler's native busy timeout blocks without yielding, which
    can deadlock a cooperative event loop (e.g. gevent) when the lock holder
    runs in another greenlet. Retry at the python level instead in that case.
    """
    try:
        from gevent.monkey import is_module_patched
    except ImportError:
        return None
    return 0.1 if is_module_patched("threading") else None


def test_concurrent_read_write(tmp_path):
    """Records emitted from several handlers while a reader is polling
    must all be inserted."""
    uri = str(tmp_path / "test.db")
    nwriters = 4
    nrecords = 20

    # Barrier which ensures that reading and writing overlaps
    started = threading.Barrier(nwriters + 1, timeout=10)

    # Publish concurrently
    def write_records(value):
        handler = Sqlite3Handler(uri, "mytable", FIELD_TYPES)
        try:
            started.wait()
            for i in range(nrecords):
                handler.handle(_make_record(field1=value, field2=str(i)))
        finally:
            handler.close()

    writer_threads = [
        threading.Thread(target=write_records, args=(value,))
        for value in range(nwriters)
    ]

    # Read concurrently
    stop_reading = threading.Event()

    def read_records():
        with sqlite3_utils.connect(uri, uri=True) as conn:
            started.wait()
            while not stop_reading.is_set():
                try:
                    _ = list(
                        sqlite3_utils.select(conn, "mytable", field_types=FIELD_TYPES)
                    )
                except sqlite3.OperationalError:
                    pass
                time.sleep(0.01)

    reader_thread = threading.Thread(target=read_records)
    reader_thread.start()
    try:
        for thread in writer_threads:
            thread.start()
        for thread in writer_threads:
            thread.join(timeout=60)
    finally:
        stop_reading.set()
        reader_thread.join(timeout=10)

    # Check that all records were published
    assert len(_select_all_records(uri)) == nwriters * nrecords


def test_write_blocked_by_reader(tmp_path):
    """A writer must wait for read locks to be released."""
    retry_period = _sqlite3_retry_period()
    lock_seconds = 0.5
    short_timeout = lock_seconds / 5  # do not retry long enough
    long_timeout = 5 * lock_seconds  # retry long enough

    # Add record to the database
    uri = str(tmp_path / "test.db")
    handler = Sqlite3Handler(uri, "mytable", FIELD_TYPES, retry_period=retry_period)
    handler.handle(_make_record(field1=1))
    handler.close()

    # Reader
    read_lock_acquired = threading.Event()

    def read_lock_database():
        conn = sqlite3.connect(uri)
        try:
            # Start read transaction
            conn.execute("BEGIN")
            conn.execute("SELECT COUNT(*) FROM mytable").fetchone()
            read_lock_acquired.set()

            # Open read transaction locks the db
            time.sleep(lock_seconds)

            # Finish transaction
            conn.rollback()
        finally:
            conn.close()

    # Write while locked: do not retry long enough
    read_lock_acquired.clear()
    thread = threading.Thread(target=read_lock_database)
    thread.start()

    handler = Sqlite3Handler(
        uri, "mytable", FIELD_TYPES, timeout=short_timeout, retry_period=retry_period
    )
    try:
        assert read_lock_acquired.wait(timeout=10)
        handler.handle(_make_record(field1=2))
    finally:
        thread.join(timeout=10)
    handler.close()

    # Write while locked: retry long enough
    read_lock_acquired.clear()
    thread = threading.Thread(target=read_lock_database)
    thread.start()

    handler = Sqlite3Handler(
        uri, "mytable", FIELD_TYPES, timeout=long_timeout, retry_period=retry_period
    )
    try:
        assert read_lock_acquired.wait(timeout=10)
        # Write while the reader locks
        handler.handle(_make_record(field1=3))
    finally:
        thread.join(timeout=10)
    handler.close()

    # Check that the expected records were published
    records = _select_all_records(uri)
    assert [record["field1"] for record in records] == [1, 3]


def _make_record(**fields) -> logging.LogRecord:
    return logging.makeLogRecord(fields)


def _select_all_records(uri: str) -> list:
    with sqlite3_utils.connect(uri, uri=True) as conn:
        return list(sqlite3_utils.select(conn, "mytable", field_types=FIELD_TYPES))
