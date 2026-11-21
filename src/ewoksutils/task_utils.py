import re
from collections.abc import Mapping
from typing import List
from typing import Optional


def task_inputs(
    id: Optional[str] = None,
    label: Optional[str] = None,
    task_identifier: Optional[str] = None,
    inputs: Optional[Mapping] = None,
) -> List[dict]:
    """Convert a {name: value} dict of inputs to a list of workflow
    inputs for given tasks.

    Provide one of ``id``, ``label`` and ``task_identifier`` to select
    the targeted tasks.

    .. code-block:: python

       inputs = task_inputs(task_identifier="SumTask", inputs={"a": 1, "b": 1})

    """
    if inputs is None:
        return []

    task_selector = {}
    if id is not None:
        task_selector["id"] = id
    if label is not None:
        task_selector["label"] = label
    if task_identifier is not None:
        task_selector["task_identifier"] = task_identifier

    return [{**task_selector, "name": k, "value": v} for k, v in inputs.items()]


def task_graph(task_identifier: str, task_type: Optional[str] = None) -> dict:
    """Return a workflow with one node that executes the task.

    .. code-block:: python

       graph = task_graph("mytasks.sumfunc")

    :param task_identifier: The task identifier.
    :param task_type: The task type. When not provided, it is guessed from the task identifier.
    """
    if task_type is None:
        task_type = guess_task_type(task_identifier)
    return {
        "graph": {"id": task_identifier},
        "nodes": [
            {
                "id": task_identifier,
                "task_type": task_type,
                "task_identifier": task_identifier,
            },
        ],
        "links": [],
    }


def guess_task_type(task_identifier: str) -> str:
    """Return the task type that matches the format of the task identifier."""
    parts = task_identifier.rsplit("::", 1)
    if len(parts) == 2 and _QUALNAME_RE.match(parts[1]):
        return "method"

    if _QUALNAME_RE.match(task_identifier):
        name = task_identifier.split(".")[-1]
        if name == "run":
            return "ppfmethod"
        elif name[0].isupper():
            return "class"
        else:
            return "method"

    if task_identifier.endswith(".ipynb"):
        return "notebook"
    else:
        return "script"


_QUALNAME_RE = re.compile(r"^[A-Za-z_]\w*(\.[A-Za-z_]\w*)*$")
