import os
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
        abspath = r"C:\abspath"
        relpath = r"relpath\file.h5"
        joinpath = "/C:/abspath/relpath/file.h5"
    else:
        abspath = "/abspath"
        relpath = "relpath/file.h5"
        joinpath = "/abspath/relpath/file.h5"

    finalpath = os.path.join(abspath, relpath)
    parsed = uri_utils.join_uri(abspath, relpath)
    assert parsed.path == joinpath
    assert str(uri_utils.path_from_uri(parsed)) == finalpath

    abspath = Path(abspath)
    relpath = Path(relpath)

    finalpath = abspath / relpath
    parsed = uri_utils.join_uri(abspath, relpath)
    assert parsed.path == joinpath
    assert uri_utils.path_from_uri(parsed) == finalpath


@pytest.mark.parametrize(
    "scheme, ext, is_file",
    [
        ("file", ".txt", False),
        ("json", ".json", True),
        ("yaml", ".yml", True),
        ("nexus", ".nx", True),
        ("hdf5", ".h5", True),
        ("https", None, False),
        ("redis", None, False),
    ],
)
def test_round_trip(scheme, ext, is_file):
    if ext:
        if sys.platform == "win32":
            uri = rf"{scheme}:///C:\path\file{ext}"
            expected = f"{scheme}:///C:/path/file{ext}"
        else:
            uri = f"{scheme}:///path/file{ext}"
            expected = uri
    else:
        uri = f"{scheme}://authority"
        expected = uri

    parsed = uri_utils.parse_uri(uri)
    final = uri_utils.uri_as_string(parsed, is_file=is_file)

    assert final == expected
