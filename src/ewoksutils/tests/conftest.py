import json
from argparse import ArgumentParser
from argparse import Namespace
from typing import Callable
from typing import List

import click
import click.testing
import pytest

from ..cli_utils.cli_argparse import add_to_parser
from ..cli_utils.cli_click import add_click_options


def argparse_interface(
    argv: List[str],
    generate_arguments: Callable[[], List],
    parse_arguments: Callable[[Namespace], None],
) -> Namespace:
    """Run a CLI defined via argparse."""
    parser = ArgumentParser()
    add_to_parser(parser, generate_arguments())
    cli_args = parser.parse_args(argv)
    parse_arguments(cli_args)
    return cli_args


def click_interface(
    argv: List[str],
    generate_arguments: Callable[[], List],
    parse_arguments: Callable[[Namespace], None],
) -> Namespace:
    """Run a CLI defined via click, returning a Namespace like argparse."""
    cli_args = None

    @click.command("test_command")
    @add_click_options(generate_arguments())
    def test_command(_cli_args: Namespace):
        nonlocal cli_args
        parse_arguments(_cli_args)
        cli_args = _cli_args

    runner = click.testing.CliRunner()
    result = runner.invoke(test_command, argv)
    if result.exception:
        raise result.exception

    return cli_args


@pytest.fixture(params=["argparse", "click"])
def cli_interface(request):
    """Yield a function that can test either the argparse or click interface."""
    if request.param == "argparse":
        yield argparse_interface
    else:
        yield click_interface


@pytest.fixture()
def graph_directory(tmp_path):
    expected_files = list()

    st_mtime = tmp_path.stat().st_mtime

    for i in range(11, 0, -1):
        filename = tmp_path / f"workflow{i}.json"
        expected_files.append(str(filename))
        st_mtime = _create_workflow(filename, {"graph": {"id": f"graph{i}"}}, st_mtime)

    subdir = tmp_path / "subdir"
    subdir.mkdir(parents=True, exist_ok=True)
    for i in range(11, 0, -1):
        filename = tmp_path / f"sub_workflow{i}.json"
        expected_files.append(str(filename))
        st_mtime = _create_workflow(
            filename, {"graph": {"id": f"sub_graph{i}"}}, st_mtime
        )

    return expected_files


def _create_workflow(filename, content, prev_st_mtime):
    while True:
        with open(filename, "w") as f:
            json.dump(content, f)
        st_mtime = filename.stat().st_mtime
        if st_mtime > prev_st_mtime:
            return st_mtime
