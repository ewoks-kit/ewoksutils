import datetime

import pytest

from .. import sqlite3_utils


def test_sqlite3_types():
    table = "test"
    field_types = {
        "num": 0,
        "real": 0.0,
        "bool": False,
        "string": "",
        "list": list(),
        "dict": dict(),
        "time": datetime.datetime.now(),
    }
    sql_types = sqlite3_utils.python_to_sql_types(field_types)

    with sqlite3_utils.connect(":memory:") as conn:
        query = sqlite3_utils.ensure_table_query(table, sql_types)
        conn.execute(query)
        conn.commit()

        query = sqlite3_utils.insert_query("test", len(field_types))

        dt1 = datetime.datetime.now()
        field_values1 = {
            "num": 10,
            "real": 1e-10,
            "bool": True,
            "string": "hello",
            "list": [1, 2, "a"],
            "dict": {"a": 1},
            "time": dt1,
        }
        row = [
            sqlite3_utils.serialize(v, sql_types[k]) for k, v in field_values1.items()
        ]
        conn.execute(query, row)

        dt2 = dt1 + datetime.timedelta(minutes=10)
        field_values2 = {
            "num": 20,
            "real": 1e-10,
            "bool": False,
            "string": "hello",
            "list": [1, 2, "a"],
            "dict": {"a": 1},
            "time": dt2,
        }
        row = [
            sqlite3_utils.serialize(v, sql_types[k]) for k, v in field_values2.items()
        ]
        conn.execute(query, row)
        conn.commit()

        rows = list(
            sqlite3_utils.select(
                conn, "test", field_types=field_types, sql_types=sql_types
            )
        )
        assert len(rows) == 2
        assert rows[0] == field_values1
        assert rows[1] == field_values2

        rows = list(
            sqlite3_utils.select(
                conn,
                "test",
                field_types=field_types,
                sql_types=sql_types,
                num=30,
            )
        )
        assert len(rows) == 0

        rows = list(
            sqlite3_utils.select(
                conn,
                "test",
                field_types=field_types,
                sql_types=sql_types,
                num=20,
            )
        )
        assert len(rows) == 1
        assert rows[0] == field_values2

        rows = list(
            sqlite3_utils.select(
                conn,
                "test",
                field_types=field_types,
                sql_types=sql_types,
                starttime=dt1,
                endtime=dt2,
            )
        )
        assert len(rows) == 2
        assert rows[0] == field_values1
        assert rows[1] == field_values2

        rows = list(
            sqlite3_utils.select(
                conn,
                "test",
                field_types=field_types,
                sql_types=sql_types,
                starttime=dt1 + datetime.timedelta(seconds=1),
            )
        )
        assert len(rows) == 1
        assert rows[0] == field_values2

        rows = list(
            sqlite3_utils.select(
                conn,
                "test",
                field_types=field_types,
                sql_types=sql_types,
                endtime=dt2 - datetime.timedelta(seconds=1),
            )
        )
        assert len(rows) == 1
        assert rows[0] == field_values1

        rows = list(
            sqlite3_utils.select(
                conn,
                "test",
                field_types=field_types,
                sql_types=sql_types,
                starttime=dt2 + datetime.timedelta(seconds=1),
            )
        )
        assert len(rows) == 0


def test_sqlite3_select_value_is_not_sql_injectable():
    """A filter value that looks like SQL must be treated as literal data,
    not executable SQL (values are passed as parameters, not interpolated)."""
    field_types = {"name": ""}
    sql_types = sqlite3_utils.python_to_sql_types(field_types)

    with sqlite3_utils.connect(":memory:") as conn:
        conn.execute(sqlite3_utils.ensure_table_query("test", sql_types))
        conn.commit()

        insert_query = sqlite3_utils.insert_query("test", len(field_types))
        conn.execute(
            insert_query, [sqlite3_utils.serialize("alice", sql_types["name"])]
        )
        conn.commit()

        malicious = "x' OR '1'='1"
        rows = list(
            sqlite3_utils.select(
                conn,
                "test",
                field_types=field_types,
                sql_types=sql_types,
                name=malicious,
            )
        )
        assert rows == []

        # The table must still exist and be queryable normally afterwards.
        rows = list(
            sqlite3_utils.select(
                conn, "test", field_types=field_types, sql_types=sql_types, name="alice"
            )
        )
        assert rows == [{"name": "alice"}]


def test_sqlite3_select_rejects_invalid_table_name():
    with sqlite3_utils.connect(":memory:") as conn:
        with pytest.raises(ValueError):
            list(sqlite3_utils.select(conn, "test; DROP TABLE test; --"))


def test_sqlite3_select_rejects_invalid_filter_key():
    with sqlite3_utils.connect(":memory:") as conn:
        with pytest.raises(ValueError):
            list(sqlite3_utils.select(conn, "test", **{"bad name; --": "value"}))
