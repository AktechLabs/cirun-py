from typing import Optional

import typer

from cirun.cloud import cloud_app
from cirun.repo import repo_app

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="Cirun CLI 🚀",
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def version(
        version_: Optional[bool] = typer.Option(
            None,
            "-v",
            "--version",
            help="Shows Cirun CLI version",
            is_eager=True,
        ),
):
    from .__about__ import __version__
    if version_:
        print(__version__)
        raise typer.Exit()


app.add_typer(repo_app, name="repo")
app.add_typer(cloud_app, name="cloud")

if __name__ == "__main__":
    app()
