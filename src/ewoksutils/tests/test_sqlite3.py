import datetime

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
