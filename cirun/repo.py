from typing_extensions import Annotated

import typer

from cirun import Cirun
from cirun.client import GH_TOKEN_ENV_VAR
from cirun.utils import OrderCommands, print_success_json, _print_error_data

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
    print_success_json(response_json)


@repo_app.command()
def add(
        name: str = RepoName,
        installation_id: Annotated[int, typer.Option(
            help=f"[Optional] GitHub installation ID for the cirun application,"
                 f"this will add repository to Cirun app installation. "
                 f"Requires {GH_TOKEN_ENV_VAR} in the environment"
        )] = None,
):
    """Activate cirun on given repository"""
    cirun = Cirun()
    response_json = cirun.set_repo(
        name,
        active=True,
        installation_id=installation_id,
        print_error=True,
    )
    print_success_json(response_json)


@repo_app.command()
def remove(name: str = RepoName):
    """Deactivate cirun on given repository"""
    cirun = Cirun()
    response_json = cirun.set_repo(name, active=False, print_error=True)
    print_success_json(response_json)
