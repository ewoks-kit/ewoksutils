from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ewoksutils")
except PackageNotFoundError:
    __version__ = "unknown"
