import requests
import typer
from rich.console import Console
from typer.core import TyperGroup

from click import Context


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


def option(name, help, *args, **kwargs):
    return typer.Option(
        ...,
        name,
        help=help,
        # show_default=False,
        *args,
        **kwargs
    )


def print_success_json(rjson):
    console = Console(style="bold green")
    console.rule("[bold green]")
    console.print_json(data=rjson)
    console.rule("[bold green]")


def _print_error(response):
    try:
        rjson = response.json()
    except requests.exceptions.JSONDecodeError:
        rjson = {
            "responseContent": response.content.decode()
        }
    return _print_error_data(data=rjson, status_code=response.status_code)


def _print_error_data(data, status_code=None):
    error_console = Console(stderr=True, style="bold red")
    error_console.rule("[bold red]")
    if isinstance(data, dict):
        error_console.print(f"Error")
        error_console.print_json(data=data)
    else:
        error_console.print(data)
    if status_code:
        error_console.log(f"Response Status Code: {status_code}")
    error_console.rule("[bold red]")
    return data
