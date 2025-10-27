from argparse import Namespace
from typing import List
from typing import Optional

from . import cli_execute_utils
from . import cli_parse
from .cli_spec import CLIArg


def submit_arguments(
    shell: bool = False,
    default_log_level: str = "warning",
    engine_names: Optional[List[str]] = None,
    graph_representations: Optional[List[str]] = None,
) -> List[CLIArg]:
    args_list = cli_execute_utils.execute_arguments(
        shell=shell,
        default_log_level=default_log_level,
        engine_names=engine_names,
        graph_representations=graph_representations,
    )
    args_list += [
        CLIArg(
            "wait",
            ["--wait"],
            help="Timeout for receiving the result. Negative number to disable.",
            type=float,
            default=-1,
        ),
        CLIArg(
            "cparameters",
            ["-c", "--cparameter"],
            help="Job scheduling parameter.",
            action="append",
            metavar="NAME=VALUE",
        ),
        CLIArg(
            "resolve_graph_remotely",
            ["--load-remote"],
            help="Load the workflow remotely instead of locally.",
            action="store_true",
        ),
    ]
    return args_list


def parse_submit_arguments(cli_args: Namespace, shell: bool = False):
    cli_execute_utils.parse_execute_argument(cli_args, shell=shell)
    cli_args.cparameters = dict(
        cli_parse.parse_option(item) for item in cli_args.cparameters
    )
