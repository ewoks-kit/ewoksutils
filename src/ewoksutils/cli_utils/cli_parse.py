import json
import os
from argparse import Namespace
from glob import glob
from json.decoder import JSONDecodeError
from typing import Any
from typing import List
from typing import Tuple


def parse_ewoks_inputs_parameters(cli_args: Namespace) -> List[dict]:
    return [
        parse_parameter(input_item, cli_args.node_attr, cli_args.inputs == "all")
        for input_item in cli_args.parameters
    ]


_NODE_ATTR_MAP = {"id": "id", "label": "label", "taskid": "task_identifier"}


def parse_parameter(input_item: str, node_attr: str, all: bool) -> dict:
    """The format of `input_item` is `"[NODE]:name=value"`"""
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
        return {"all": all, "name": var_name, "value": var_value}
    return {
        _NODE_ATTR_MAP[node_attr]: node,
        "name": var_name,
        "value": var_value,
    }


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
