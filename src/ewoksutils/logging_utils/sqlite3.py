import sqlite3
import time
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from .. import sqlite3_utils
from .connection import ConnectionHandler

Sqlite3RecordType = List[Any]


class Sqlite3Handler(ConnectionHandler):
    def __init__(self, uri: str, table: str, field_types: Dict):
        self._uri = uri
        self._field_sql_types = sqlite3_utils.python_to_sql_types(field_types)
        self._ensure_table_query = sqlite3_utils.ensure_table_query(
            table, self._field_sql_types
        )
        self._insert_row_query = sqlite3_utils.insert_query(
            table, len(self._field_sql_types)
        )
        self._connection_context = None
        super().__init__()

    def _connect(self, timeout=1) -> None:
        if self._connection is not None:
            raise RuntimeError("Already connected")
        ctx = None
        try:
            ctx = sqlite3_utils.connect(
                self._uri, timeout=timeout, uri=True, check_same_thread=False
            )
            conn = ctx.__enter__()
            self._sql_query(self._ensure_table_query, conn=conn)
        except (OSError, TimeoutError):
            if ctx is not None:
                ctx.__exit__(None, None, None)
            self._connection = None
            self._connection_context = None
        else:
            self._connection = conn
            self._connection_context = ctx

    def _disconnect(self) -> None:
        self._connection_context.__exit__(None, None, None)

    def _send_serialized_record(self, values: Optional[Sqlite3RecordType]):
        if values:
            self._sql_query(self._insert_row_query, values)

    def _serialize_record(self, record) -> Optional[Sqlite3RecordType]:
        lst = list()
        for field, sql_type in self._field_sql_types.items():
            value = getattr(record, field, None)
            lst.append(sqlite3_utils.serialize(value, sql_type))
        return lst

    def _sql_query(
        self,
        sql: str,
        parameters: Sequence = tuple(),
        conn: Optional[sqlite3.Connection] = None,
        timeout=1,
    ) -> None:
        if conn is None:
            conn = self._connection
        exception = None
        t0 = time.time()
        while True:
            try:
                conn.execute(sql, parameters)
                break
            except sqlite3.OperationalError as e:
                exception = e
            t1 = time.time()
            if timeout is not None and (t1 - t0) > timeout:
                raise TimeoutError("cannot execute SQL query") from exception
        while True:
            try:
                conn.commit()
                break
            except sqlite3.OperationalError as e:
                exception = e
            t1 = time.time()
            if timeout is not None and (t1 - t0) > timeout:
                raise TimeoutError("cannot commit SQL query") from exception
