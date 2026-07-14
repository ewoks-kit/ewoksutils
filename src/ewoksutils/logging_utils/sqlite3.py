import sqlite3
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
    ):
        """
        :param uri: for example "file:/path/to/test.db" or "file:///path/to/test.db".
        :param table: name of the database table in which records are inserted
                      (the table is created when missing).
        :param field_types: mapping from record attribute names (table columns)
                            to python types.
        :param timeout: native sqlite3 busy timeout: the maximum time to wait
                        for database locks to be released by other connections.
                        A record is dropped when the timeout is reached.
        :param disconnect_on_error: disconnect when emitting a record failed.
        """
        super().__init__(disconnect_on_error=disconnect_on_error)
        self._uri = uri
        self._timeout = timeout
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
        ctx = sqlite3_utils.connect(
            self._uri, timeout=self._timeout, uri=True, check_same_thread=False
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
