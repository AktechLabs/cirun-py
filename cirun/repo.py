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
        install_github_app: Annotated[bool, typer.Option(
            "--install-github-app",
            help=f"Add repository to Cirun app installation. "
                 f"Requires {GH_TOKEN_ENV_VAR} in the environment and "
                 "installation-id option",
        )] = False,
        installation_id: Annotated[int, typer.Option(
            help=f"GitHub installation ID "
        )] = None,
):
    """Activate cirun on given repository"""
    cirun = Cirun()
    if install_github_app and not installation_id:
        return _print_error_data("ERROR: 'installation-id' is required, when "
                                 "'--install-github-app' option is specified")

    response_json = cirun.set_repo(
        name,
        active=True,
        install_github_app=install_github_app,
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
