from argparse import Namespace
from typing import List
from typing import Optional

from . import cli_arguments
from . import cli_log_utils
from . import cli_parse
from .cli_spec import CLIArg


def execute_arguments(
    shell: bool = False,
    default_log_level: str = "warning",
    engine_names: Optional[List[str]] = None,
    graph_representations: Optional[List[str]] = None,
) -> List[CLIArg]:
    if shell:
        args_list = cli_log_utils.log_arguments(default_log_level=default_log_level)
    else:
        args_list = []
    args_list += cli_arguments.workflow_arguments("execute")
    args_list += cli_arguments.ewoks_inputs_arguments()
    args_list += [
        CLIArg(
            "representation",
            ["--workflow-format"],
            help="Source format. Ignored when --test is provided.",
            type=str.lower,
            default="",
            choices=graph_representations,
        ),
        CLIArg(
            "data_root_uri",
            ["--data-root-uri"],
            help="Root for Ewoks task result caching.",
            default="",
        ),
        CLIArg(
            "data_scheme",
            ["--data-scheme"],
            help="Data format for Ewoks task result caching.",
            choices=["nexus", "json"],
            default="nexus",
        ),
        CLIArg(
            "options",
            ["-o", "--option"],
            help="Engine execution option.",
            action="append",
            metavar="OPTION=VALUE",
        ),
        CLIArg(
            "task_options",
            ["-t", "--task-option"],
            help="Ewoks task option.",
            action="append",
            metavar="OPTION=VALUE",
        ),
        CLIArg(
            "job_id",
            ["-j", "--jobid"],
            help="Job ID for Ewoks events.",
            default=None,
        ),
        CLIArg(
            "disable_events",
            ["--disable-events"],
            help="Disable Ewoks events",
            action="store_true",
        ),
        CLIArg(
            "sqlite3_uri",
            ["--sqlite3"],
            help="Store Ewoks events in an SQLite3 DB.",
            default=None,
        ),
        CLIArg(
            "outputs",
            ["--outputs"],
            help="Print Ewoks task outputs.",
            choices=["none", "end", "all"],
            default="none",
        ),
        CLIArg(
            "merge_outputs",
            ["--merge-outputs"],
            help="Print merged Ewoks task outputs.",
            action="store_true",
        ),
        CLIArg(
            "engine",
            ["--engine"],
            help="Execution engine.",
            choices=engine_names,
            default="core",
        ),
    ]
    return args_list


def parse_execute_argument(cli_args: Namespace, shell: bool = False):
    if shell:
        cli_log_utils.parse_log_arguments(cli_args)
    cli_args.workflows, cli_args.graphs = cli_parse.parse_workflows(cli_args)

    inputs = cli_parse.parse_ewoks_inputs_parameters(cli_args)

    if cli_args.outputs == "all":
        outputs = [{"all": True}]
    elif cli_args.outputs == "end":
        outputs = [{"all": False}]
    else:
        outputs = []

    varinfo = {
        "root_uri": cli_args.data_root_uri,
        "scheme": cli_args.data_scheme,
    }

    load_options = {}
    if cli_args.root_module:
        load_options["root_module"] = cli_args.root_module
    if cli_args.root_dir:
        load_options["root_dir"] = cli_args.root_dir
    if cli_args.representation:
        load_options["representation"] = cli_args.representation
    if cli_args.test:
        load_options["representation"] = "test_core"

    execinfo = dict()
    if cli_args.job_id:
        execinfo["job_id"] = cli_args.job_id
    if cli_args.sqlite3_uri:
        # TODO: asynchronous handling may loose events
        execinfo["asynchronous"] = False
        execinfo["handlers"] = [
            {
                "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
                "arguments": [{"name": "uri", "value": cli_args.sqlite3_uri}],
            }
        ]

    task_options = dict(cli_parse.parse_option(item) for item in cli_args.task_options)

    execute_options = dict(cli_parse.parse_option(item) for item in cli_args.options)
    execute_options["inputs"] = inputs
    execute_options["outputs"] = outputs
    execute_options["merge_outputs"] = cli_args.merge_outputs
    execute_options["load_options"] = load_options
    execute_options["varinfo"] = varinfo
    execute_options["execinfo"] = execinfo
    execute_options["task_options"] = task_options

    cli_args.execute_options = execute_options
