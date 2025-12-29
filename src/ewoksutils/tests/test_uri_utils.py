import os
import sys
from pathlib import Path

import pytest

from .. import uri_utils


@pytest.mark.skipif(
    sys.version_info >= (3, 12, 5), reason="Behaviour changes in python3.12.5"
)
def test_relpath_file_uri_old():
    nonpath = str(Path("file.h5"))
    relpath = str(Path("relpath") / "file.h5")
    assert not os.path.isabs(nonpath)
    assert not os.path.isabs(relpath)

    uri = nonpath
    assert uri_utils.parse_uri(uri).geturl() == "file:///file.h5"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = relpath
    assert uri_utils.parse_uri(uri).geturl() == "file:///relpath/file.h5"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = nonpath + "::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:///file.h5?path=/entry"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == nonpath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}

    uri = relpath + "::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:///relpath/file.h5?path=/entry"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == relpath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}


@pytest.mark.skipif(
    sys.version_info < (3, 12, 5), reason="Behaviour changes in python3.12.5"
)
def test_relpath_file_uri():
    nonpath = str(Path("file.h5"))
    relpath = str(Path("relpath") / "file.h5")
    assert not os.path.isabs(nonpath)
    assert not os.path.isabs(relpath)

    uri = nonpath
    assert uri_utils.parse_uri(uri).geturl() == "file:file.h5"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = relpath
    assert uri_utils.parse_uri(uri).geturl() == "file:relpath/file.h5"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = nonpath + "::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:file.h5?path=/entry"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == nonpath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}

    uri = relpath + "::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:relpath/file.h5?path=/entry"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == relpath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}


def test_abspath_uri():
    abspath = str(Path(os.path.sep) / "abspath" / "file.h5")
    assert os.path.isabs(abspath)

    uri = abspath
    assert uri_utils.parse_uri(uri).geturl() == "file:///abspath/file.h5"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == uri
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == dict()

    uri = abspath + "::/entry"
    assert uri_utils.parse_uri(uri).geturl() == "file:///abspath/file.h5?path=/entry"
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == abspath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {"path": "/entry"}

    uri = abspath + "::/entry?name=abc"
    assert (
        uri_utils.parse_uri(uri).geturl()
        == "file:///abspath/file.h5?path=/entry&name=abc"
    )
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == abspath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {
        "path": "/entry",
        "name": "abc",
    }

    uri = abspath + "::/entry?path=xyz&name=abc"
    assert (
        uri_utils.parse_uri(uri).geturl()
        == "file:///abspath/file.h5?path=/entry/xyz&name=abc"
    )
    assert str(uri_utils.path_from_uri(uri_utils.parse_uri(uri))) == abspath
    assert uri_utils.parse_query(uri_utils.parse_uri(uri)) == {
        "path": "/entry/xyz",
        "name": "abc",
    }
