import os
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Iterable
from typing import Tuple
from typing import Union

_WIN32 = sys.platform == "win32"


def parse_uri(
    uri: str,
    default_scheme: str = "file",
    default_port: int = None,
) -> urllib.parse.ParseResult:
    """The general structure of a URI is:
    scheme://netloc/path;parameters?query#frag
    """
    uri, query_paths = _normalize(uri)
    result = urllib.parse.urlparse(uri)
    scheme, netloc, path, params, query, fragment = result
    if _WIN32 and len(scheme) == 1:
        result = urllib.parse.urlparse(f"file://{uri}")
        scheme, netloc, path, params, query, fragment = result
    query = _merge_query(query_paths, query)
    if not scheme and default_scheme:
        scheme = default_scheme
    if default_port and not result.port:
        netloc = f"{result.hostname}:{default_port}"
    return type(result)(scheme, netloc, path, params, query, fragment)


def path_from_uri(uri: Union[str, urllib.parse.ParseResult], **parse_options) -> Path:
    if isinstance(uri, str):
        uri = parse_uri(uri, **parse_options)
    return Path(uri.netloc) / uri.path


def parse_query(uri: Union[str, urllib.parse.ParseResult], **parse_options) -> dict:
    if isinstance(uri, str):
        uri = parse_uri(uri, **parse_options)
    return _split_query(uri.query)


def join_uri(
    root: Union[str, urllib.parse.ParseResult],
    relative: Union[str, urllib.parse.ParseResult],
    **parse_options,
) -> urllib.parse.ParseResult:
    if isinstance(root, str):
        root = parse_uri(root, **parse_options)
    if isinstance(relative, str):
        relative = parse_uri(relative, **parse_options)
    if root.params or relative.params:
        raise NotImplementedError()
    path = os.path.join(root.path, relative.path)
    query = _merge_query(root.query, relative.query)
    return urllib.parse.ParseResult(root.scheme, root.netloc, path, "", query, "")


def uri_as_string(uri: Union[str, urllib.parse.ParseResult]) -> str:
    if isinstance(uri, urllib.parse.ParseResult):
        return uri.geturl()
    return uri


def _normalize(uri: str) -> Tuple[str, str]:
    uri = uri.replace("\\", "/")
    # Non-standard notation:
    #   "/some/path::/another/path"
    # means
    #   "/some/path?path=/another/path"
    query = ""
    query_paths = re.findall("::([^;?#]*)", uri)
    if query_paths:
        for path in query_paths:
            uri = uri.replace("::" + path, "")
        query = _join_query(("path", path) for path in query_paths)
    return uri, query


def _split_query(query: str) -> dict:
    result = dict()
    for s in query.split("&"):
        if not s:
            continue
        name, _, value = s.partition("=")
        prev_value = result.get(name)
        if prev_value:
            value = _join_string(prev_value, value, "/")
        result[name] = value
    return result


def _join_query(query_items: Iterable[Tuple[str, str]]) -> str:
    return "&".join(f"{k}={v}" for k, v in query_items)


def _join_string(a: str, b: str, sep: str):
    aslash = a.endswith(sep)
    bslash = b.startswith(sep)
    if aslash and bslash:
        return a[:-1] + b
    elif aslash or bslash:
        return a + b
    else:
        return a + sep + b


def _merge_query(query1: str, query2: str) -> str:
    query1 = _split_query(query1)
    query2 = _split_query(query2)
    merged = list()
    names = list(query1) + list(query2)
    for name in names:
        value1 = query1.pop(name, None)
        value2 = query2.pop(name, None)
        if value1 and value2:
            merged.append((name, _join_string(value1, value2, "/")))
        elif value1:
            merged.append((name, value1))
        elif value2:
            merged.append((name, value2))
    return _join_query(merged)
