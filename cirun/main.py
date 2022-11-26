import typer

from cirun.cloud import cloud_app
from cirun.repo import repo_app

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

app.add_typer(repo_app, name="repo")
app.add_typer(cloud_app, name="cloud")

if __name__ == "__main__":
    app()
