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


def option(name, help, *args, **kwargs):
    return typer.Option(
        ...,
        name,
        help=help,
        show_default=False,
        *args, **kwargs
    )


@cloud_connect.command()
def aws(
        access_key=option("--access-key", help="AWS_ACCESS_KEY_ID"),
        secret_key=option("--secret-key", help="AWS_SECRET_ACCESS_KEY"),
):
    """Connect AWS to Cirun"""
    credentials = {
        "access_key": access_key,
        "secret_key": secret_key
    }
    _connect_cloud(name="aws", credentials=credentials)


@cloud_connect.command()
def azure(
        subscription_id=option("--subscription-id", help="Azure subscription_id"),
        tenant_id=option("--tenant-id", help="Azure tenant_id"),
        client_id=option("--client-id", help="Azure client_id"),
        client_secret=option("--client-secret", help="Azure client_secret"),
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
        service_account_file=option("--key-file", help="GCP Service Account Key file",),
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
        username=option("--username", help="OpenStack username"),
        password=option("--password", help="OpenStack password"),
        auth_url=option("--auth-url", help="OpenStack auth_url"),
        project_id=option("--project-id", help="OpenStack project_id"),
        domain_id=option("--domain-id", help="OpenStack domain_id"),
        network=option("--network", help="OpenStack network"),
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


@cloud_connect.command()
def oracle(
        config_file=option("--config-file", help="Oracle config file, it should have the keys: "
                                                 "'user', 'tenancy', 'compartment_id', 'fingerprint'"),
        key_file=option("--key-file", help="Oracle private key"),
):
    """Connect Oracle to Cirun"""
    credentials = {
        "config": open(config_file, 'r').read(),
        "private_key": open(key_file, 'r').read(),
    }
    _connect_cloud(name="oracle", credentials=credentials)


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
