from numbers import Integral, Real
import json
from datetime import datetime
from typing import Any, Dict, Iterator
from .datetime_utils import fromisoformat


def ensure_table_query(table: str, field_sql_types: Dict[str, str]) -> str:
    s = f"CREATE TABLE IF NOT EXISTS {table}"
    if not field_sql_types:
        return s
    columns = [f"{k} {v}" for k, v in field_sql_types.items()]
    columns = ", ".join(columns)
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


def python_to_sql_types(data: Dict) -> str:
    return {k: python_to_sql_type(v) for k, v in data.items()}


def serialize(value, sql_type: str):
    if value is not None:
        vsql_type = python_to_sql_type(value)
        if sql_type != vsql_type:
            raise TypeError("wrong SQL type")
    if isinstance(value, (Integral, Real, bool, str)):
        return value
    elif isinstance(value, datetime):
        return value.isoformat()
    else:
        return json.dumps(value).encode()


def deserialize(value, python_type):
    if value == b"null":
        return None
    elif isinstance(python_type, bool):
        return bool(value)
    elif isinstance(python_type, (Integral, Real, str)):
        return value
    elif isinstance(python_type, datetime):
        return fromisoformat(value)
    else:
        return json.loads(value.decode())


def select(
    conn,
    field_types: Dict,
    sql_types: Dict,
    starttime=None,
    endtime=None,
    **is_equal_filter,
) -> Iterator[dict]:
    cursor = conn.cursor()

    if is_equal_filter:
        conditions = [
            f"{k} = {serialize(v, sql_types[k])}" for k, v in is_equal_filter.items()
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
        conditions = " AND ".join(conditions)
        query = f"SELECT * FROM test WHERE {conditions}"
    else:
        query = "SELECT * FROM test"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.commit()

    fields = [col[0] for col in cursor.description]
    for values in rows:
        yield {k: deserialize(v, field_types[k]) for k, v in zip(fields, values)}
