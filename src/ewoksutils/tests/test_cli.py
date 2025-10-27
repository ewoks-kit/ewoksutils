from ..cli_utils import cli_cancel_utils
from ..cli_utils import cli_execute_utils
from ..cli_utils import cli_submit_utils


def test_cli_execute(cli_interface):
    argv = [
        "acyclic1",
        "acyclic2",
        "--test",
        "-p",
        "a=1",
        "-p",
        "task1:b=test",
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
        "inputs": [
            {"all": False, "name": "a", "value": 1},
            {"id": "task1", "name": "b", "value": "test"},
        ],
        "merge_outputs": False,
        "outputs": [],
        "task_options": {},
        "varinfo": {"root_uri": "", "scheme": "nexus"},
        "load_options": {"representation": "test_core", "root_dir": "/tmp"},
        "execinfo": {},
    }
    assert cli_args.execute_options == execute_options


def test_cli_submit(cli_interface):
    argv = [
        "acyclic1",
        "acyclic2",
        "--test",
        "-p",
        "a=1",
        "-p",
        "task1:b=test",
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
            {"all": False, "name": "a", "value": 1},
            {"id": "task1", "name": "b", "value": "test"},
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
