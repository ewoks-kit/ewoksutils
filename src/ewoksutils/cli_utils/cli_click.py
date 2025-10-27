from argparse import Namespace
from functools import wraps
from typing import List

import click

from .cli_spec import CLIArg


def add_click_options(args_list: List[CLIArg]):
    """
    Decorator factory that adds Click arguments/options from a list of CLIArg objects.

    Example:
        @click.command("mycommand")
        @add_click_options([...])
        def mycommand(cli_args: Namespace):
            print(cli_args)
    """

    def decorator(func):
        param_to_attr = {}
        pos_names = []
        for cli_arg in reversed(args_list):
            param_name = cli_arg.dest
            if "-" in param_name:
                raise ValueError(
                    f"{cli_arg.dest!r} is not a valid python variable name"
                )

            param_to_attr[param_name] = param_name
            for flag in cli_arg.flags:
                arg_name = flag.lstrip("-").replace("-", "_")
                param_to_attr[arg_name] = param_name

            # Shared properties
            click_kwargs = {"help": cli_arg.help}
            if cli_arg.default is not None:
                click_kwargs["default"] = cli_arg.default
                click_kwargs["show_default"] = True
            if cli_arg.required:
                click_kwargs["required"] = True
            if cli_arg.metavar:
                click_kwargs["metavar"] = cli_arg.metavar

            # Handle argument types
            if callable(cli_arg.type):
                click_kwargs["type"] = cli_arg.type
            if cli_arg.choices:
                click_kwargs["type"] = click.Choice(cli_arg.choices)
            if cli_arg.action:
                if cli_arg.action in ("store_true", "store_false"):
                    click_kwargs["is_flag"] = True
                elif cli_arg.action == "append":
                    click_kwargs["multiple"] = True
                else:
                    raise ValueError(f"{cli_arg.action!r} action is not supported")

            # Handle nargs
            if cli_arg.nargs is None:
                pass
            elif cli_arg.nargs == "+":
                click_kwargs["nargs"] = -1
                click_kwargs["required"] = True
            elif cli_arg.nargs == "*":
                click_kwargs["nargs"] = -1
            elif isinstance(cli_arg.nargs, int):
                click_kwargs["nargs"] = cli_arg.nargs
            else:
                raise ValueError(
                    f"Unsupported CLI argument value: nargs={cli_arg.nargs}"
                )

            if cli_arg.is_positional:
                arg_kwargs = {
                    k: v
                    for k, v in click_kwargs.items()
                    if k not in ("help", "show_default")
                }
                func = click.argument(param_name, **arg_kwargs)(func)
                pos_names.append(param_name)
            else:
                func = click.option(*cli_arg.flags, **click_kwargs)(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Convert position to named
            if args:
                if len(pos_names) != len(args):
                    raise RuntimeError(
                        f"CLI: expected {len(pos_names)} arguments but got {len(args)}"
                    )
                kwargs.update(zip(pos_names, args))

            # Convert click name to destination
            attrs = {}
            for name, value in kwargs.items():
                attrs[param_to_attr[name]] = value

            namespace = Namespace(**attrs)
            return func(namespace)

        return wrapper

    return decorator
