import pytest

from ..task_utils import task_inputs


@pytest.mark.parametrize("selector", ["id", "label", "task_identifier"])
def test_task_inputs(selector):
    inputs = task_inputs(**{selector: "task"}, inputs={"a": 1, "b": "test"})
    assert inputs == [
        {selector: "task", "name": "a", "value": 1},
        {selector: "task", "name": "b", "value": "test"},
    ]
