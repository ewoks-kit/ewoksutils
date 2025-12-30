import re
import sys
import urllib.parse
from pathlib import Path
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Union

_WIN32 = sys.platform == "win32"


def parse_uri(
    uri: Union[str, Path],
    default_scheme: str = "file",
    default_port: Optional[int] = None,
) -> urllib.parse.ParseResult:
    """
    Parse a URI following RFC 3986 rules.

    The scheme and path components are required, though the path may be empty.
    When authority is present, the path must either be empty or begin with "/".
    When authority is not present, the path cannot begin with "//".
    """
    uri, query_paths = _normalize(uri)

    parsed = urllib.parse.urlparse(uri)
    scheme, netloc, path, params, query, fragment = parsed

    query = _merge_query(query_paths, query)

    if not scheme and default_scheme:
        scheme = default_scheme
    if default_port and not parsed.port:
        netloc = f"{parsed.hostname}:{default_port}"

    return urllib.parse.ParseResult(scheme, netloc, path, params, query, fragment)


def path_from_uri(
    uri: Union[str, Path, urllib.parse.ParseResult], **parse_options
) -> Path:
    if not isinstance(uri, urllib.parse.ParseResult):
        uri = parse_uri(uri, **parse_options)
    return Path(_file_path_from_parsed(uri))


def parse_query(
    uri: Union[str, Path, urllib.parse.ParseResult], **parse_options
) -> dict:
    if not isinstance(uri, urllib.parse.ParseResult):
        uri = parse_uri(uri, **parse_options)
    return _split_query(uri.query)


def join_uri(
    root: Union[str, Path, urllib.parse.ParseResult],
    relative: Union[str, Path, urllib.parse.ParseResult],
    **parse_options,
) -> urllib.parse.ParseResult:
    if not isinstance(root, urllib.parse.ParseResult):
        root = parse_uri(root, **parse_options)
    if not isinstance(relative, urllib.parse.ParseResult):
        relative = parse_uri(relative, **parse_options)

    if root.params or relative.params:
        raise NotImplementedError("URI params are not supported")

    relative_path = _file_path_from_parsed(relative)
    path = f"{root.path}/{relative_path}"

    query = _merge_query(root.query, relative.query)

    return urllib.parse.ParseResult(root.scheme, root.netloc, path, "", query, "")


def uri_as_string(uri: Union[str, Path, urllib.parse.ParseResult]) -> str:
    if isinstance(uri, str):
        return uri
    if isinstance(uri, Path):
        uri = parse_uri(uri)
    if not isinstance(uri, urllib.parse.ParseResult):
        raise TypeError(type(uri))

    if not uri.netloc:
        tmp_uri = urllib.parse.ParseResult(
            "file", uri.netloc, uri.path, uri.params, uri.query, uri.fragment
        )
        uri_str = tmp_uri.geturl()
        return uri_str.replace("file://", f"{uri.scheme}://", 1)

    return uri.geturl()


def _normalize(uri: Union[str, Path]) -> Tuple[str, str]:
    """Handle URI's that do not follow the RFC 3986 rules."""

    uri = str(uri).replace("\\", "/")  # Handle Windows paths

    # Windows drive-letter path handling (C:/..., D:/...)
    if _WIN32 and re.match(r"^[A-Za-z]:/", uri):
        uri = f"file:///{uri}"

    # Non-standard notation:
    #   "/some/path::/another/path"
    # becomes:
    #   "/some/path?path=/another/path"
    query = ""
    query_paths = re.findall(r"::([^;?#]*)", uri)
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


def _join_string(a: str, b: str, sep: str) -> str:
    aslash = a.endswith(sep)
    bslash = b.startswith(sep)
    if aslash and bslash:
        return a[:-1] + b
    if aslash or bslash:
        return a + b
    return a + sep + b


def _merge_query(query1: str, query2: str) -> str:
    query1 = _split_query(query1)
    query2 = _split_query(query2)
    merged = []

    for name in list(query1) + list(query2):
        value1 = query1.pop(name, None)
        value2 = query2.pop(name, None)
        if value1 and value2:
            merged.append((name, _join_string(value1, value2, "/")))
        elif value1:
            merged.append((name, value1))
        elif value2:
            merged.append((name, value2))

    return _join_query(merged)


def _file_path_from_parsed(uri: urllib.parse.ParseResult) -> str:
    if _WIN32 and uri.path.startswith("/"):
        return uri.path[1:]
    return uri.path
