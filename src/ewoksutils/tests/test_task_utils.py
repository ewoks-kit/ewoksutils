import pytest

from ..task_utils import guess_task_type
from ..task_utils import task_graph
from ..task_utils import task_inputs


@pytest.mark.parametrize("selector", ["id", "label", "task_identifier"])
def test_task_inputs(selector):
    inputs = task_inputs(**{selector: "task"}, inputs={"a": 1, "b": "test"})
    assert inputs == [
        {selector: "task", "name": "a", "value": 1},
        {selector: "task", "name": "b", "value": "test"},
    ]


@pytest.mark.parametrize(
    "task_identifier,task_type",
    [
        ("mymodule.MyTask", "class"),
        ("mymodule.myfunc", "method"),
        ("mymodule.run", "ppfmethod"),
        ("/path/to/script.py::myfunc", "method"),
        ("/path/to/script.py", "script"),
        ("/path/to/notebook.ipynb", "notebook"),
    ],
)
def test_guess_task_type(task_identifier, task_type):
    assert guess_task_type(task_identifier) == task_type


def test_task_graph():
    assert task_graph("mymodule.myfunc") == {
        "graph": {"id": "mymodule.myfunc"},
        "nodes": [
            {
                "id": "mymodule.myfunc",
                "task_type": "method",
                "task_identifier": "mymodule.myfunc",
            }
        ],
        "links": [],
    }
