from collections.abc import Mapping
from typing import List
from typing import Optional

__all__ = ["task_inputs"]


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
