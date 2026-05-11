import json
import logging
import os
import warnings
from argparse import Namespace
from glob import glob
from json.decoder import JSONDecodeError
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

logger = logging.getLogger(__name__)


def parse_ewoks_inputs_parameters(cli_args: Namespace) -> List[dict]:
    parameters = []

    # Deprecated options

    if cli_args.parameters:
        replacement = {"id": "-pn", "label": "-pl", "taskid": "-pt"}[cli_args.node_attr]

        if cli_args.inputs == "all":
            default_target = "-pa"
        else:
            default_target = "-ps"

        _deprecated(
            f"-p/--parameter is deprecated; "
            f"use {replacement} for node-specific parameters "
            f"and {default_target} for parameters without a node selector."
        )

        if cli_args.node_attr != "id":
            replacement = {"label": "-pl", "taskid": "-pt"}[cli_args.node_attr]

            _deprecated(
                f"--input-node-id={cli_args.node_attr} is deprecated; "
                f"use {replacement} instead."
            )

        if cli_args.inputs != "start":
            replacement = {"start": "-ps", "all": "-pa"}[cli_args.inputs]

            _deprecated(
                f"--inputs={cli_args.inputs} is deprecated; "
                f"use {replacement} instead."
            )

        parameters.extend(
            parse_parameter(
                input_item,
                node_attr=cli_args.node_attr,
                all_nodes=(cli_args.inputs == "all"),
            )
            for input_item in cli_args.parameters
        )

    parameters.extend(
        parse_parameter(input_item, node_attr="id")
        for input_item in cli_args.parameters_nodeid
    )

    parameters.extend(
        parse_parameter(input_item, node_attr="taskid")
        for input_item in cli_args.parameters_taskid
    )

    parameters.extend(
        parse_parameter(input_item, node_attr="label")
        for input_item in cli_args.parameters_label
    )

    parameters.extend(
        parse_parameter(input_item, all_nodes=False)
        for input_item in cli_args.parameters_start
    )

    parameters.extend(
        parse_parameter(input_item, all_nodes=True)
        for input_item in cli_args.parameters_all
    )

    return parameters


def _deprecated(message: str) -> None:
    warnings.warn(message, DeprecationWarning, stacklevel=3)
    logger.warning(message)


_NODE_ATTR_MAP = {"id": "id", "label": "label", "taskid": "task_identifier"}


def parse_parameter(
    input_item: str, node_attr: Optional[str] = None, all_nodes: Optional[bool] = None
) -> dict:
    """The format of `input_item` is `"[NODE:]NAME=VALUE"`."""

    node_and_name, _, value = input_item.partition("=")
    a, sep, b = node_and_name.partition(":")

    if sep:
        node = a
        var_name = b
    else:
        node = None
        var_name = a

    var_value = parse_value(value)

    if node is None:
        if all_nodes is None:
            raise ValueError(f"{input_item} needs a target NODE:{input_item}")
        return {"all": all_nodes, "name": var_name, "value": var_value}

    if node_attr is None and node is not None:
        raise ValueError(f"{input_item} does not need the target '{node}'")

    return {_NODE_ATTR_MAP[node_attr]: node, "name": var_name, "value": var_value}


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
