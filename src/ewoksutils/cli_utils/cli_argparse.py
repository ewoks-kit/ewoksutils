import argparse
from typing import List

from .cli_spec import CLIArg


def add_to_parser(parser: argparse.ArgumentParser, args_list: List[CLIArg]) -> None:
    """Render abstract args into an argparse parser.

    .. code-block:: python

        parser = argparse.ArgumentParser(description="CLI interface")

        subparsers = parser.add_subparsers(help="Commands", dest="command")
        mycommand = subparsers.add_parser(
            "mycommand",
            help="Description of command",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        add_to_parser(mycommand, [...])
    """
    for cli_arg in args_list:
        if "-" in cli_arg.dest:
            raise ValueError(f"{cli_arg.dest!r} is not a valid python variable name")

        kwargs = {"help": cli_arg.help}
        if cli_arg.default is not None:
            kwargs["default"] = cli_arg.default
        if cli_arg.choices is not None:
            kwargs["choices"] = cli_arg.choices
        if cli_arg.metavar is not None:
            kwargs["metavar"] = cli_arg.metavar
        if cli_arg.nargs is not None:
            kwargs["nargs"] = cli_arg.nargs
        if cli_arg.required is not None:
            kwargs["required"] = cli_arg.required
        if cli_arg.action is not None:
            kwargs["action"] = cli_arg.action
        if cli_arg.type is not None:
            kwargs["type"] = cli_arg.type

        if cli_arg.is_positional:
            parser.add_argument(cli_arg.dest, **kwargs)
        else:
            parser.add_argument(*cli_arg.flags, dest=cli_arg.dest, **kwargs)
