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
            "parameters_nodeid",
            ["-pn", "--parameter-nodeid"],
            help="Input variable for a node addressed by node id.",
            action="append",
            metavar="[NODE_ID:]NAME=VALUE",
        ),
        CLIArg(
            "parameters_taskid",
            ["-pt", "--parameter-taskid"],
            help="Input variable for a node addressed by task identifier.",
            action="append",
            metavar="[TASK_ID:]NAME=VALUE",
        ),
        CLIArg(
            "parameters_label",
            ["-pl", "--parameter-label"],
            help="Input variable for a node addressed by node label.",
            action="append",
            metavar="[LABEL:]NAME=VALUE",
        ),
        CLIArg(
            "parameters_start",
            ["-ps", "--parameter-start"],
            help="Input variable for all start nodes.",
            action="append",
            metavar="NAME=VALUE",
        ),
        CLIArg(
            "parameters_all",
            ["-pa", "--parameter-all"],
            help="Input variable for all nodes.",
            action="append",
            metavar="NAME=VALUE",
        ),
        # Deprecated legacy option
        CLIArg(
            "parameters",
            ["-p", "--parameter"],
            help=(
                "DEPRECATED: use -pn/-pt/-pl/-ps/-pa instead. "
                "Input variable for a particular node "
                "(or start/all nodes when missing depending on --inputs)."
            ),
            action="append",
            metavar="[NODE:]NAME=VALUE",
        ),
        CLIArg(
            "node_attr",
            ["--input-node-id"],
            help=(
                "DEPRECATED: use -pn/-pt/-pl instead. "
                "The NODE attribute used when specifying an input parameter."
            ),
            choices=["id", "label", "taskid"],
            default="id",
        ),
        CLIArg(
            "inputs",
            ["--inputs"],
            help=(
                "DEPRECATED: use -ps/-pa instead. "
                "Inputs without a specific node go to start/all nodes."
            ),
            choices=["start", "all"],
            default="start",
        ),
    ]
