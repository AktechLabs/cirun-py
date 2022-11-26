import json

import typer
from rich.console import Console

from cirun import Cirun
from cirun.utils import OrderCommands

cloud_app = typer.Typer(
    cls=OrderCommands,
    help="Manage cloud providers",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)

cloud_connect = typer.Typer(
    cls=OrderCommands,
    help="Connect cloud providers",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)


cloud_app.add_typer(cloud_connect, name="connect")


@cloud_connect.command()
def aws(
        access_key=typer.Option(
            None,
            "--access-key",
            help="AWS_ACCESS_KEY_ID",
            is_eager=True,
        ),
        secret_key=typer.Option(
            None,
            "--secret-key",
            help="AWS_SECRET_ACCESS_KEY",
            is_eager=True,
        ),
):
    """Connect AWS to Cirun"""
    credentials = {
        "access_key": access_key,
        "secret_key": secret_key
    }
    _connect_cloud(name="aws", credentials=credentials)


@cloud_connect.command()
def azure(
        subscription_id=typer.Option(None, "--subscription-id", help="Azure subscription_id", is_eager=True),
        tenant_id=typer.Option(None, "--tenant-id", help="Azure tenant_id", is_eager=True),
        client_id=typer.Option(None, "--client-id", help="Azure client_id", is_eager=True),
        client_secret=typer.Option(None, "--client-secret", help="Azure client_secret", is_eager=True),
):
    """Connect Azure cloud to Cirun"""
    credentials = {
        "subscription_id": subscription_id,
        "tenant_id": tenant_id,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    _connect_cloud(name="azure", credentials=credentials)


@cloud_connect.command()
def gcp(
        service_account_file=typer.Option(None, "--key-file", help="GCP Service Account Key file", is_eager=True),
):
    """Connect GCP to Cirun"""
    service_account_txt = open(service_account_file, 'r').read()
    try:
        credentials = json.loads(service_account_txt)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid key file: {service_account_file}")
    _connect_cloud(name="gcp", credentials=credentials)


@cloud_connect.command()
def openstack(
        username=typer.Option(None, "--username", help="OpenStack username", is_eager=True),
        password=typer.Option(None, "--password", help="OpenStack password", is_eager=True),
        auth_url=typer.Option(None, "--auth-url", help="OpenStack auth_url", is_eager=True),
        project_id=typer.Option(None, "--project-id", help="OpenStack project_id", is_eager=True),
        domain_id=typer.Option(None, "--domain-id", help="OpenStack domain_id", is_eager=True),
        network=typer.Option(None, "--network", help="OpenStack network", is_eager=True),
):
    """Connect Openstack to Cirun"""
    credentials = {
        "username": username,
        "password": password,
        "auth_url": auth_url,
        "project_id": project_id,
        "domain_id": domain_id,
        "network": network,
    }
    _connect_cloud(name="openstack", credentials=credentials)


def _connect_cloud(name, credentials):
    cirun = Cirun()
    response_json = cirun.cloud_connect(
        name=name,
        credentials=credentials,
        print_error=True
    )
    console = Console(style="bold green")
    console.rule("[bold green]")
    console.print_json(data=response_json)
    console.rule("[bold green]")
