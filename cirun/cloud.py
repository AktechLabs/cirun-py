import json
import subprocess

import typer
from rich.console import Console

from cirun import Cirun
from cirun.utils import OrderCommands, option

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

cloud_create = typer.Typer(
    cls=OrderCommands,
    help="Create cloud provider credentials",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)


cloud_app.add_typer(cloud_connect, name="connect")
cloud_app.add_typer(cloud_create, name="create")


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


@cloud_connect.command(name="azure")
def connect_azure(
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
        service_account_file=option("--key-file", help="GCP Service Account Key file", ),
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


@cloud_create.command(name="azure")
def create_azure(
        name: str = typer.Option(
            None,
            "--name",
            help="Name for the service principal (optional, auto-generated if not provided)"
        ),
        auto_connect: bool = typer.Option(
            False,
            "--auto-connect",
            help="Automatically connect the created credentials to Cirun"
        ),
):
    """Create Azure Service Principal credentials for Cirun"""
    import os

    console = Console()
    error_console = Console(stderr=True, style="bold red")

    if auto_connect and not os.environ.get("CIRUN_API_KEY"):
        error_console.print("Error: CIRUN_API_KEY environment variable is required for --auto-connect")
        raise typer.Exit(code=1)

    # Check if Azure CLI is installed
    try:
        subprocess.run(
            ["az", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        error_console.print("Error: Azure CLI is not installed or not found in PATH")
        error_console.print("Install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        raise typer.Exit(code=1)

    # Check if user is logged in and get account details
    console.print("[bold blue]Checking Azure CLI login status...[/bold blue]")
    try:
        result = subprocess.run(
            ["az", "account", "show", "--output", "json"],
            capture_output=True,
            check=True,
            text=True
        )
        account_info = json.loads(result.stdout)
    except subprocess.CalledProcessError:
        error_console.print("Error: Not logged in to Azure CLI")
        error_console.print("Please run: az login")
        raise typer.Exit(code=1)

    # Display account details
    console.print("\n[bold green]Azure Account Details:[/bold green]")
    console.print(f"  Account Name:      [bold]{account_info.get('user', {}).get('name', 'N/A')}[/bold]")
    console.print(f"  Subscription Name: [bold]{account_info.get('name', 'N/A')}[/bold]")
    console.print(f"  Subscription ID:   [bold]{account_info.get('id', 'N/A')}[/bold]")
    console.print(f"  Tenant ID:         [bold]{account_info.get('tenantId', 'N/A')}[/bold]")
    console.print(f"  State:             [bold]{account_info.get('state', 'N/A')}[/bold]")
    console.print("")

    subscription_id = account_info.get('id')

    # Generate service principal name if not provided
    if not name:
        from datetime import datetime, timezone
        name = f"cirun-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    # Confirm before creating
    typer.confirm(
        f"Create service principal '{name}' with contributor role on subscription '{subscription_id}'?",
        abort=True,
    )

    # Create service principal
    console.print(f"[bold blue]Creating service principal '[bold green]{name}[/bold green]'...[/bold blue]")
    try:
        result = subprocess.run(
            [
                "az", "ad", "sp", "create-for-rbac",
                "--name", name,
                "--role", "contributor",
                "--scopes", f"/subscriptions/{subscription_id}",
                "--output", "json"
            ],
            capture_output=True,
            check=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        error_console.print(f"Error creating service principal: {e.stderr}")
        raise typer.Exit(code=1)

    # Parse output
    sp_data = json.loads(result.stdout)
    client_id = sp_data.get("appId")
    client_secret = sp_data.get("password")
    tenant_id = sp_data.get("tenant")

    # Display credentials
    success_console = Console(style="bold green")
    success_console.rule("[bold green]")
    success_console.print("[bold green]✓[/bold green] Service principal created successfully!")
    success_console.print("")
    success_console.print("[bold yellow]Azure Credentials for Cirun:[/bold yellow]")
    success_console.print("")
    success_console.print(f"AZURE_SUBSCRIPTION_ID: [bold]{subscription_id}[/bold]")
    success_console.print(f"AZURE_CLIENT_ID:       [bold]{client_id}[/bold]")
    success_console.print(f"AZURE_CLIENT_SECRET:   [bold]{client_secret}[/bold]")
    success_console.print(f"AZURE_TENANT_ID:       [bold]{tenant_id}[/bold]")
    success_console.print("")
    success_console.print("[bold red]⚠️  Save the CLIENT_SECRET - it won't be shown again![/bold red]")
    success_console.rule("[bold green]")

    # Auto-connect if requested
    if auto_connect:
        console.print("\n[bold blue]Connecting credentials to Cirun...[/bold blue]")
        credentials = {
            "subscription_id": subscription_id,
            "tenant_id": tenant_id,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        _connect_cloud(name="azure", credentials=credentials)


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
