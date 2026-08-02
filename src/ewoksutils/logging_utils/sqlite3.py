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
    def __init__(
        self,
        uri: str,
        table: str,
        field_types: Dict,
        timeout: float = 10,
        disconnect_on_error: bool = False,
        retry_period: Optional[float] = None,
    ):
        """
        :param uri: for example "file:/path/to/test.db" or "file:///path/to/test.db".
        :param table: name of the database table in which records are inserted
                      (the table is created when missing).
        :param field_types: mapping from record attribute names (table columns)
                            to python types.
        :param timeout: maximum time to wait for database locks to be released
                        by other connections. A record is dropped when the
                        timeout is reached.
        :param disconnect_on_error: disconnect when emitting a record failed.
        :param retry_period: when `None` (default), `timeout` is used as sqlite3's
                        native busy timeout. When set, retrying is done at the
                        python level instead.
        """
        super().__init__(disconnect_on_error=disconnect_on_error)
        self._uri = uri
        self._timeout = timeout
        self._retry_period = retry_period
        self._field_sql_types = sqlite3_utils.python_to_sql_types(field_types)

        self._ensure_table_query = sqlite3_utils.ensure_table_query(
            table, self._field_sql_types
        )
        self._insert_row_query = sqlite3_utils.insert_query(
            table, len(self._field_sql_types)
        )

        self._connection = None
        self._connection_context = None

    def _connect(self) -> None:
        if self._retry_period is None:
            native_timeout = self._timeout
        else:
            native_timeout = min(self._timeout, self._retry_period)
        ctx = sqlite3_utils.connect(
            self._uri,
            timeout=native_timeout,
            uri=True,
            check_same_thread=False,
        )
        try:
            conn = ctx.__enter__()
            self._sql_query(self._ensure_table_query, conn=conn)
        except BaseException:
            ctx.__exit__(None, None, None)
            self._connection = None
            self._connection_context = None
            raise
        self._connection = conn
        self._connection_context = ctx

    def _disconnect(self) -> None:
        self._connection_context.__exit__(None, None, None)
        self._connection = None
        self._connection_context = None

    def _connected(self) -> bool:
        return self._connection is not None

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
    ) -> None:
        if conn is None:
            conn = self._connection
        if conn is None:
            raise RuntimeError("Sqlite3Handler is not connected")
        if self._retry_period is None:
            self._sql_query_single_attempt(sql, parameters, conn)
        else:
            self._sql_query_with_retries(sql, parameters, conn, self._retry_period)

    @staticmethod
    def _sql_query_single_attempt(
        sql: str, parameters: Sequence, conn: sqlite3.Connection
    ) -> None:
        try:
            conn.execute(sql, parameters)
            conn.commit()
        except BaseException:
            # Do not leave the failed query pending in an open transaction.
            try:
                conn.rollback()
            except sqlite3.OperationalError:
                pass
            raise

    def _sql_query_with_retries(
        self,
        sql: str,
        parameters: Sequence,
        conn: sqlite3.Connection,
        retry_period: float,
    ) -> None:
        start = time.time()
        while True:
            try:
                conn.execute(sql, parameters)
                conn.commit()
                return
            except BaseException as ex:
                # Do not leave the failed query pending in an open transaction.
                try:
                    conn.rollback()
                except sqlite3.OperationalError:
                    pass

                # retry when certain exceptions
                do_retry = self._retry_sqlite3_exception(ex)
                if do_retry and time.time() - start < self._timeout:
                    time.sleep(retry_period)
                    continue

                raise

    @staticmethod
    def _retry_sqlite3_exception(ex: BaseException) -> bool:
        if not isinstance(ex, sqlite3.OperationalError):
            return False
        error_message = str(ex)
        if "database is locked" in error_message:
            # transient lock by another connection.
            return True
        return False
