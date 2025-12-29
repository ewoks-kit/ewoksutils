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
    assert uri_utils.parse_uri(uri).geturl() == "file:///file.h5"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = relpath
    assert uri_utils.parse_uri(uri).geturl() == "file:///relpath/file.h5"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = f"{nonpath}::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:///file.h5?path=/entry"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == nonpath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}

    uri = f"{relpath}::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:///relpath/file.h5?path=/entry"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == relpath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}


@pytest.mark.skipif(
    sys.version_info < (3, 12, 5), reason="Behaviour changes in python3.12.5"
)
def test_relpath_file_uri():
    nonpath = Path("file.h5")
    relpath = Path("relpath") / "file.h5"
    assert not nonpath.is_absolute()
    assert not relpath.is_absolute()

    uri = nonpath
    assert uri_utils.parse_uri(uri).geturl() == "file:file.h5"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = relpath
    assert uri_utils.parse_uri(uri).geturl() == "file:relpath/file.h5"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = f"{nonpath}::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:file.h5?path=/entry"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == nonpath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}

    uri = f"{relpath}::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:relpath/file.h5?path=/entry"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == relpath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}


def test_abspath_uri():
    abspath = Path(os.path.sep) / "abspath" / "file.h5"
    assert abspath.is_absolute()

    uri = abspath
    assert uri_utils.parse_uri(uri).geturl() == "file:///abspath/file.h5"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = f"{abspath}::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:///abspath/file.h5?path=/entry"
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == abspath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}

    uri = f"{abspath}::/entry?name=abc"
    assert (
        uri_utils.parse_uri(uri).geturl()
        == "file:///abspath/file.h5?path=/entry&name=abc"
    )
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == abspath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {
        "path": "/entry",
        "name": "abc",
    }

    uri = f"{abspath}::/entry?path=xyz&name=abc"
    assert (
        uri_utils.parse_uri(uri).geturl()
        == "file:///abspath/file.h5?path=/entry/xyz&name=abc"
    )
    assert uri_utils.path_from_uri(uri_utils.parse_uri(uri)) == abspath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {
        "path": "/entry/xyz",
        "name": "abc",
    }
