import pytest

from ..cli_utils import cli_cancel_utils
from ..cli_utils import cli_execute_utils
from ..cli_utils import cli_submit_utils


def test_cli_execute_no_parameters(cli_interface):
    argv = [
        "acyclic1",
        "acyclic2",
        "--test",
        "--workflow-dir",
        "/tmp",
    ]
    cli_args = cli_interface(
        argv,
        cli_execute_utils.execute_arguments,
        cli_execute_utils.parse_execute_argument,
    )

    assert list(cli_args.graphs) == ["acyclic1", "acyclic2"]

    execute_options = {
        "inputs": [],
        "merge_outputs": False,
        "outputs": [],
        "task_options": {},
        "varinfo": {"root_uri": "", "scheme": "nexus"},
        "load_options": {"representation": "test_core", "root_dir": "/tmp"},
        "execinfo": {},
    }
    assert cli_args.execute_options == execute_options


def test_cli_execute_parameters(cli_interface):
    argv = [
        "acyclic1",
        "--test",
        "-ps",
        "a=1",
        "-pa",
        "b=2",
        "-pn",
        "node1:c=3",
        "-pt",
        "task1:d=4",
        "-pl",
        "label1:e=5",
    ]

    cli_args = cli_interface(
        argv,
        cli_execute_utils.execute_arguments,
        cli_execute_utils.parse_execute_argument,
    )

    execute_options = {
        "inputs": [
            {"id": "node1", "name": "c", "value": 3},
            {"task_identifier": "task1", "name": "d", "value": 4},
            {"label": "label1", "name": "e", "value": 5},
            {"all": False, "name": "a", "value": 1},
            {"all": True, "name": "b", "value": 2},
        ],
        "merge_outputs": False,
        "outputs": [],
        "task_options": {},
        "varinfo": {"root_uri": "", "scheme": "nexus"},
        "load_options": {"representation": "test_core"},
        "execinfo": {},
    }

    assert cli_args.execute_options == execute_options


@pytest.mark.parametrize("argument", ["pn", "pt", "pl"])
def test_cli_execute_missing_parameter_target(cli_interface, argument):
    argv = ["acyclic1", "--test", f"-{argument}", "a=1"]  # This is missing a target

    with pytest.raises(ValueError, match="a=1 needs a target NODE:a=1"):
        _ = cli_interface(
            argv,
            cli_execute_utils.execute_arguments,
            cli_execute_utils.parse_execute_argument,
        )


@pytest.mark.parametrize("argument", ["ps", "pa"])
def test_cli_execute_unexpected_parameter_target(cli_interface, argument):
    argv = [
        "acyclic1",
        "--test",
        f"-{argument}",
        "node1:a=1",  # This has un unexpected target
    ]

    with pytest.raises(ValueError, match="node1:a=1 does not accept a target"):
        _ = cli_interface(
            argv,
            cli_execute_utils.execute_arguments,
            cli_execute_utils.parse_execute_argument,
        )


def test_cli_execute_deprecated_parameters(cli_interface):
    argv = ["acyclic1", "--test", "-p", "a=1", "-p", "task1:b=test"]

    with pytest.deprecated_call(match="-p/--parameter is deprecated"):
        cli_args = cli_interface(
            argv,
            cli_execute_utils.execute_arguments,
            cli_execute_utils.parse_execute_argument,
        )

    assert list(cli_args.graphs) == ["acyclic1"]

    execute_options = {
        "inputs": [
            {"all": False, "name": "a", "value": 1},
            {"id": "task1", "name": "b", "value": "test"},
        ],
        "merge_outputs": False,
        "outputs": [],
        "task_options": {},
        "varinfo": {"root_uri": "", "scheme": "nexus"},
        "load_options": {"representation": "test_core"},
        "execinfo": {},
    }

    assert cli_args.execute_options == execute_options


def test_cli_execute_deprecated_input_node_id(cli_interface):
    argv = [
        "acyclic1",
        "--test",
        "--input-node-id",
        "taskid",
        "-p",
        "task1:b=test",
    ]

    with pytest.deprecated_call(match="-p/--parameter is deprecated"):
        with pytest.deprecated_call(match="--input-node-id=taskid is deprecated"):
            cli_args = cli_interface(
                argv,
                cli_execute_utils.execute_arguments,
                cli_execute_utils.parse_execute_argument,
            )

    execute_options = {
        "inputs": [
            {
                "task_identifier": "task1",
                "name": "b",
                "value": "test",
            }
        ],
        "merge_outputs": False,
        "outputs": [],
        "task_options": {},
        "varinfo": {"root_uri": "", "scheme": "nexus"},
        "load_options": {"representation": "test_core"},
        "execinfo": {},
    }

    assert cli_args.execute_options == execute_options


def test_cli_execute_deprecated_inputs_all(cli_interface):
    argv = [
        "acyclic1",
        "--test",
        "--inputs",
        "all",
        "-p",
        "a=1",
    ]

    with pytest.deprecated_call(match="-p/--parameter is deprecated"):
        with pytest.deprecated_call(match="--inputs=all is deprecated"):
            cli_args = cli_interface(
                argv,
                cli_execute_utils.execute_arguments,
                cli_execute_utils.parse_execute_argument,
            )

    execute_options = {
        "inputs": [
            {"all": True, "name": "a", "value": 1},
        ],
        "merge_outputs": False,
        "outputs": [],
        "task_options": {},
        "varinfo": {"root_uri": "", "scheme": "nexus"},
        "load_options": {"representation": "test_core"},
        "execinfo": {},
    }

    assert cli_args.execute_options == execute_options


def test_cli_submit(cli_interface):
    argv = [
        "acyclic1",
        "acyclic2",
        "--test",
        "-ps",
        "a=1",
        "-pn",
        "node1:b=test",
        "--workflow-dir",
        "/tmp",
        "--wait=inf",
    ]
    cli_args = cli_interface(
        argv,
        cli_submit_utils.submit_arguments,
        cli_submit_utils.parse_submit_arguments,
    )

    assert list(cli_args.graphs) == ["acyclic1", "acyclic2"]

    execute_options = {
        "inputs": [
            {"id": "node1", "name": "b", "value": "test"},
            {"all": False, "name": "a", "value": 1},
        ],
        "merge_outputs": False,
        "outputs": [],
        "task_options": {},
        "varinfo": {"root_uri": "", "scheme": "nexus"},
        "load_options": {"representation": "test_core", "root_dir": "/tmp"},
        "execinfo": {},
    }
    assert cli_args.execute_options == execute_options

    assert cli_args.wait == float("inf")


def test_cli_execute_search(cli_interface, tmp_path, graph_directory):
    argv = [
        str(tmp_path / "subdir" / "*.json"),
        str(tmp_path / "*.json"),
        "--search",
    ]
    cli_args = cli_interface(
        argv,
        cli_execute_utils.execute_arguments,
        cli_execute_utils.parse_execute_argument,
    )

    assert len(cli_args.graphs) == 22
    assert cli_args.graphs == graph_directory


def test_cli_submit_search(cli_interface, tmp_path, graph_directory):
    argv = [
        str(tmp_path / "subdir" / "*.json"),
        str(tmp_path / "*.json"),
        "--search",
        "--wait=inf",
    ]
    cli_args = cli_interface(
        argv,
        cli_submit_utils.submit_arguments,
        cli_submit_utils.parse_submit_arguments,
    )

    assert len(cli_args.graphs) == 22
    assert cli_args.graphs == graph_directory

    assert cli_args.wait == float("inf")


def test_cli_cancel(cli_interface):
    argv = ["id1", "id2"]
    cli_args = cli_interface(
        argv,
        cli_cancel_utils.cancel_arguments,
        cli_cancel_utils.parse_cancel_arguments,
    )

    assert list(cli_args.job_ids) == ["id1", "id2"]
