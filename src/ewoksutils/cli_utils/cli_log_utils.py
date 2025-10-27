import logging
import sys
from argparse import Namespace
from typing import List

from .cli_spec import CLIArg

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def log_arguments(default_log_level: str = "warning") -> List[CLIArg]:
    return [
        CLIArg(
            "log",
            ["-l", "--log"],
            help="Log level.",
            type=str.lower,
            choices=list(LEVELS),
            default=default_log_level,
        )
    ]


def parse_log_arguments(cli_args: Namespace) -> None:
    logger = logging.getLogger()
    level = LEVELS[cli_args.log]
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s"
    )

    class StdOutFilter(logging.Filter):
        def filter(self, record):
            return record.levelno < logging.WARNING

    class StdErrFilter(logging.Filter):
        def filter(self, record):
            return record.levelno >= logging.WARNING

    if level < logging.WARNING:
        h = logging.StreamHandler(sys.stdout)
        h.addFilter(StdOutFilter())
        h.setLevel(level)
        if formatter is not None:
            h.setFormatter(formatter)
        logger.addHandler(h)

    h = logging.StreamHandler(sys.stderr)
    h.addFilter(StdErrFilter())
    h.setLevel(level)
    if formatter is not None:
        h.setFormatter(formatter)
    logger.addHandler(h)
