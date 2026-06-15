import json
import logging
import os
import warnings
from argparse import Namespace
from glob import glob
from json.decoder import JSONDecodeError
from typing import Any
from typing import List
from typing import Tuple

logger = logging.getLogger(__name__)


def parse_ewoks_inputs_parameters(cli_args: Namespace) -> List[dict]:
    parameters = []

    # Deprecated options

    if cli_args.parameters:
        node_attr_replacement = {"id": "-pn", "label": "-pl", "taskid": "-pt"}
        node_attr_default_value = "id"
        inputs_replacement = {"start": "-ps", "all": "-pa"}
        inputs_default_value = "start"

        # Deprecate -p
        replacement = node_attr_replacement[cli_args.node_attr]

        if cli_args.inputs == "all":
            default_target = "-pa"
        else:
            default_target = "-ps"

        _deprecated(
            f"-p/--parameter is deprecated; "
            f"use {replacement} for node-specific parameters "
            f"and {default_target} for parameters without a node selector."
        )

        # Deprecate --input-node-id when used
        if cli_args.node_attr != node_attr_default_value:
            replacement = node_attr_replacement[cli_args.node_attr]

            _deprecated(
                f"--input-node-id={cli_args.node_attr} is deprecated; "
                f"use {replacement} instead."
            )

        # Deprecate --inputs when used
        if cli_args.inputs != inputs_default_value:
            replacement = inputs_replacement[cli_args.inputs]

            _deprecated(
                f"--inputs={cli_args.inputs} is deprecated; use {replacement} instead."
            )

        all_nodes = cli_args.inputs == "all"
        for input_item in cli_args.parameters:
            if parameter_has_target(input_item):
                param = parse_targeted_parameter(input_item, cli_args.node_attr)
            else:
                param = parse_untargeted_parameter(input_item, all_nodes=all_nodes)
            parameters.append(param)

    parameters.extend(
        parse_targeted_parameter(input_item, "id")
        for input_item in cli_args.parameters_nodeid
    )

    parameters.extend(
        parse_targeted_parameter(input_item, "taskid")
        for input_item in cli_args.parameters_taskid
    )

    parameters.extend(
        parse_targeted_parameter(input_item, "label")
        for input_item in cli_args.parameters_label
    )

    parameters.extend(
        parse_untargeted_parameter(input_item, all_nodes=False)
        for input_item in cli_args.parameters_start
    )

    parameters.extend(
        parse_untargeted_parameter(input_item, all_nodes=True)
        for input_item in cli_args.parameters_all
    )

    return parameters


def _deprecated(message: str) -> None:
    warnings.warn(message, DeprecationWarning, stacklevel=3)
    logger.warning(message)


_NODE_ATTR_MAP = {"id": "id", "label": "label", "taskid": "task_identifier"}


def parse_targeted_parameter(input_item: str, node_attr: str) -> dict:
    """Parse `NODE:NAME=VALUE`."""

    node_and_var_name, _, var_value = input_item.partition("=")
    node, sep, var_name = node_and_var_name.partition(":")

    if not sep:
        raise ValueError(f"{input_item} needs a target NODE:{input_item}")

    return {
        _NODE_ATTR_MAP[node_attr]: node,
        "name": var_name,
        "value": parse_value(var_value),
    }


def parse_untargeted_parameter(input_item: str, all_nodes: bool) -> dict:
    """Parse `NAME=VALUE`."""

    var_name, _, var_value = input_item.partition("=")
    _, sep, _ = var_name.partition(":")

    if sep:
        raise ValueError(f"{input_item} does not accept a target node")

    return {
        "all": all_nodes,
        "name": var_name,
        "value": parse_value(var_value),
    }


def parameter_has_target(input_item: str) -> bool:
    """Check whether `"[NODE]:name=value"` has a target NODE."""
    node_and_var_name, _, _ = input_item.partition("=")
    _, sep, _ = node_and_var_name.partition(":")
    return bool(sep)


def parse_option(option: str) -> Tuple[str, Any]:
    option, _, value = option.partition("=")
    return option, parse_value(value)


def parse_value(value: str) -> Any:
    try:
        return json.loads(value)
    except JSONDecodeError:
        return value


def parse_workflows(cli_args: Namespace) -> Tuple[List[str], List[str]]:
    """
    :returns: workflows (possibly expanded due the search),
              graphs (execute graph arguments)
    """
    if not cli_args.search or cli_args.test:
        return cli_args.workflows, cli_args.workflows

    parsed_workflows = list()
    files = (filename for workflow in cli_args.workflows for filename in glob(workflow))

    for filename in sorted(files, key=os.path.getmtime):
        if filename not in parsed_workflows:
            parsed_workflows.append(filename)

    return parsed_workflows, parsed_workflows
