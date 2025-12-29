import json
import sqlite3
from contextlib import closing
from contextlib import contextmanager
from datetime import datetime
from numbers import Integral
from numbers import Real
from typing import Any
from typing import Dict
from typing import Generator
from typing import Iterator
from typing import Optional
from typing import Union

from . import uri_utils
from .datetime_utils import fromisoformat


def ensure_table_query(table: str, field_sql_types: Dict[str, str]) -> str:
    s = f"CREATE TABLE IF NOT EXISTS {table}"
    if not field_sql_types:
        return s
    lst = [f"{k} {v}" for k, v in field_sql_types.items()]
    columns = ", ".join(lst)
    return f"{s} ({columns})"


def insert_query(table: str, nfields: int):
    values = ("?," * nfields)[:-1]
    return f"INSERT INTO {table} VALUES({values})"


def python_to_sql_type(value: Any) -> str:
    if isinstance(value, (Integral, bool)):
        return "INTEGER"
    elif isinstance(value, Real):
        return "REAL"
    elif isinstance(value, (str, datetime)):
        return "TEXT"
    else:
        return "BLOB"


def python_to_sql_types(field_types: Optional[Dict]) -> dict:
    if not field_types:
        return dict()
    return {k: python_to_sql_type(v) for k, v in field_types.items()}


def serialize(value: Any, sql_type: Optional[str] = None):
    if value is not None and sql_type is not None:
        vsql_type = python_to_sql_type(value)
        if sql_type != vsql_type:
            raise TypeError(f"value {value} does not have SQL type {sql_type}")
    if isinstance(value, (Integral, Real, bool, str)):
        return value
    elif isinstance(value, datetime):
        return value.isoformat()
    else:
        return json.dumps(value).encode()


def _select_serialize(value: Any, sql_type: Optional[str] = None):
    sql_value = serialize(value, sql_type)
    if isinstance(sql_value, str):
        return f"'{sql_value}'"
    return sql_value


def deserialize(sql_value, field_type: Optional[str] = None):
    if isinstance(sql_value, bytes):
        sql_value = sql_value.decode()
    if sql_value == "null" or sql_value is None:
        return None
    elif isinstance(field_type, bool):
        return bool(sql_value)
    elif isinstance(field_type, (Integral, Real, str)):
        return sql_value
    elif isinstance(field_type, datetime):
        return fromisoformat(sql_value)
    else:
        return json.loads(sql_value)


def select(
    conn,
    table: str,
    field_types: Optional[Dict] = None,
    sql_types: Optional[Dict] = None,
    starttime: Optional[Union[str, datetime]] = None,
    endtime: Optional[Union[str, datetime]] = None,
    **is_equal_filter,
) -> Iterator[dict]:
    if is_equal_filter:
        if sql_types is None:
            sql_types = python_to_sql_types(field_types)
        conditions = [
            f"{k} = {_select_serialize(v, sql_types.get(k))}"
            for k, v in is_equal_filter.items()
        ]
    else:
        conditions = list()

    if starttime:
        if isinstance(starttime, str):
            starttime = fromisoformat(starttime)
        conditions.append(f"time >= '{starttime.isoformat()}'")

    if endtime:
        if isinstance(endtime, str):
            endtime = fromisoformat(endtime)
        conditions.append(f"time <= '{endtime.isoformat()}'")

    if conditions:
        search_condition = " AND ".join(conditions)
        query = f"SELECT * FROM {table} WHERE {search_condition}"
    else:
        query = f"SELECT * FROM {table}"

    with closing(conn.cursor()) as cursor:
        try:
            cursor.execute(query)
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                return
            raise  # Re-raise other errors

        rows = cursor.fetchall()
        conn.commit()

        if cursor.description is None:
            return

        fields = [col[0] for col in cursor.description]
        if field_types is None:
            field_types = {}

        for values in rows:
            yield {
                k: deserialize(v, field_types.get(k)) for k, v in zip(fields, values)
            }


@contextmanager
def connect(database: str, **kwargs) -> Generator[sqlite3.Connection, None, None]:
    if database != ":memory:":
        _ensure_directory_exists(database)
    with closing(sqlite3.connect(database, **kwargs)) as conn:
        yield conn


def _ensure_directory_exists(uri: str) -> None:
    parsed = uri_utils.parse_uri(uri)
    if parsed.scheme == "file":
        path = uri_utils.path_from_uri(uri)
        path.parent.mkdir(parents=True, exist_ok=True)
