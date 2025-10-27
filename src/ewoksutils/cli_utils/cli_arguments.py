from typing import List

from .cli_spec import CLIArg


def workflow_arguments(action: str) -> List[CLIArg]:
    return [
        CLIArg(
            "workflows",
            [],
            help=f"Workflow(s) to {action} (e.g. JSON filename, JSON string).",
            nargs="+",
        ),
        CLIArg(
            "test",
            ["--test"],
            help="The 'workflow' argument refers to the name of a test graph.",
            action="store_true",
        ),
        CLIArg(
            "search",
            ["--search"],
            help="The 'workflow' argument is a pattern to search for."
            "Ignored when --test is provided.",
            action="store_true",
        ),
        CLIArg(
            "root_dir",
            ["--workflow-dir"],
            help="Directory for path-like workflow representations or "
            "task identifiers of sub-workflows (cwd by default).",
        ),
        CLIArg(
            "root_module",
            ["--workflow-module"],
            help="Python root module for module-like workflow representations or "
            "task identifiers of sub-workflows (cwd by default).",
        ),
    ]


def ewoks_inputs_arguments() -> List[CLIArg]:
    return [
        CLIArg(
            "parameters",
            ["-p", "--parameter"],
            help="Input variable for a particular node"
            " (or all start nodes when missing)",
            action="append",
            metavar="[NODE:]NAME=VALUE",
        ),
        CLIArg(
            "node_attr",
            ["--input-node-id"],
            help="The NODE attribute used when specifying an input parameter",
            choices=["id", "label", "taskid"],
            default="id",
        ),
        CLIArg(
            "inputs",
            ["--inputs"],
            help="Inputs without a specific node go to start/all nodes",
            choices=["start", "all"],
            default="start",
        ),
    ]
