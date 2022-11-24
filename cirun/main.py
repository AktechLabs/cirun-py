import typer
from click import Context
from rich.console import Console
from typer.core import TyperGroup

from cirun.client import Cirun


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)


repo_app = typer.Typer(
    cls=OrderCommands,
    help="Manage Repository Activation/Deactivation",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

RepoName = typer.Argument(
    default=None,
    help=f"Repository Name, for example: cirunlabs/cirun",
    is_eager=True
)


@repo_app.command("list")
def list_():
    """Activate cirun on given repository"""
    cirun = Cirun()
    response_json = cirun.get_repos(print_error=True)
    console = Console(style="bold green")
    console.rule("[bold green]")
    console.print_json(data=response_json)
    console.rule("[bold green]")


@repo_app.command()
def add(name: str = RepoName):
    """Activate cirun on given repository"""
    cirun = Cirun()
    response_json = cirun.set_repo(name, active=True, print_error=True)
    console = Console(style="bold green")
    console.rule("[bold green]")
    console.print_json(data=response_json)
    console.rule("[bold green]")


@repo_app.command()
def remove(name: str = RepoName):
    """Deactivate cirun on given repository"""
    cirun = Cirun()
    response_json = cirun.set_repo(name, active=False, print_error=True)
    console = Console(style="bold green")
    console.rule("[bold green]")
    console.print_json(data=response_json)
    console.rule("[bold green]")


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)
app.add_typer(repo_app, name="repo")


if __name__ == "__main__":
    repo_app()
