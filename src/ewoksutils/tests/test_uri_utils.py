import sys
from pathlib import Path

import pytest

from .. import uri_utils


@pytest.mark.skipif(
    sys.version_info >= (3, 12, 5), reason="Behaviour changes in python3.12.5"
)
def test_relpath_file_uri_old():
    nonpath = Path("file.h5")
    relpath = Path("relpath") / "file.h5"
    assert not nonpath.is_absolute()
    assert not relpath.is_absolute()

    uri = nonpath
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == "file:///file.h5"
    assert uri_utils.path_from_uri(parsed) == uri
    assert uri_utils.parse_query(parsed) == dict()

    uri = relpath
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == "file:///relpath/file.h5"
    assert uri_utils.path_from_uri(parsed) == uri
    assert uri_utils.parse_query(parsed) == dict()

    uri = f"{nonpath}::/entry"
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == "file:///file.h5?path=/entry"
    assert uri_utils.path_from_uri(parsed) == nonpath
    assert uri_utils.parse_query(parsed) == {"path": "/entry"}

    uri = f"{relpath}::/entry"
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == "file:///relpath/file.h5?path=/entry"
    assert uri_utils.path_from_uri(parsed) == relpath
    assert uri_utils.parse_query(parsed) == {"path": "/entry"}


@pytest.mark.skipif(
    sys.version_info < (3, 12, 5), reason="Behaviour changes in python3.12.5"
)
def test_relpath_file_uri():
    nonpath = Path("file.h5")
    relpath = Path("relpath") / "file.h5"
    assert not nonpath.is_absolute()
    assert not relpath.is_absolute()

    uri = nonpath
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == "file:file.h5"
    assert uri_utils.path_from_uri(parsed) == uri
    assert uri_utils.parse_query(parsed) == dict()

    uri = relpath
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == "file:relpath/file.h5"
    assert uri_utils.path_from_uri(parsed) == uri
    assert uri_utils.parse_query(parsed) == dict()

    uri = f"{nonpath}::/entry"
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == "file:file.h5?path=/entry"
    assert uri_utils.path_from_uri(parsed) == nonpath
    assert uri_utils.parse_query(parsed) == {"path": "/entry"}

    uri = f"{relpath}::/entry"
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == "file:relpath/file.h5?path=/entry"
    assert uri_utils.path_from_uri(parsed) == relpath
    assert uri_utils.parse_query(parsed) == {"path": "/entry"}


def test_abspath_uri():
    if sys.platform == "win32":
        abspath = Path(r"C:\abspath\file.h5")
        expected_base_uri = "file:///C:/abspath/file.h5"
    else:
        abspath = Path("/abspath/file.h5")
        expected_base_uri = "file:///abspath/file.h5"
    assert abspath.is_absolute()

    uri = abspath
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == expected_base_uri
    assert uri_utils.path_from_uri(parsed) == abspath
    assert uri_utils.parse_query(parsed) == {}

    uri = f"{abspath}::/entry"
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == f"{expected_base_uri}?path=/entry"
    assert uri_utils.path_from_uri(parsed) == abspath
    assert uri_utils.parse_query(parsed) == {"path": "/entry"}

    uri = f"{abspath}::/entry?name=abc"
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == f"{expected_base_uri}?path=/entry&name=abc"
    assert uri_utils.path_from_uri(parsed) == abspath
    assert uri_utils.parse_query(parsed) == {
        "path": "/entry",
        "name": "abc",
    }

    uri = f"{abspath}::/entry?path=xyz&name=abc"
    parsed = uri_utils.parse_uri(uri)
    assert parsed.geturl() == f"{expected_base_uri}?path=/entry/xyz&name=abc"
    assert uri_utils.path_from_uri(parsed) == abspath
    assert uri_utils.parse_query(parsed) == {
        "path": "/entry/xyz",
        "name": "abc",
    }


def test_join_uri():
    if sys.platform == "win32":
        abspath = Path(r"C:\abspath")
    else:
        abspath = Path("/abspath")
    assert abspath.is_absolute()

    relpath = Path("relpath") / "file.h5"
    assert not relpath.is_absolute()

    parsed = uri_utils.join_uri(abspath, relpath)
    assert uri_utils.path_from_uri(parsed) == abspath / relpath
