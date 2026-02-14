import json
import subprocess
import time

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


@cloud_create.command(name="aws")
def create_aws(
        name: str = typer.Option(
            None,
            "--name",
            help="Name for the IAM user (optional, auto-generated if not provided)"
        ),
        policy_arn: str = typer.Option(
            "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
            "--policy-arn",
            help="IAM policy ARN to attach to the user"
        ),
        auto_connect: bool = typer.Option(
            False,
            "--auto-connect",
            help="Automatically connect the created credentials to Cirun"
        ),
):
    """Create AWS IAM User credentials for Cirun"""
    import os

    console = Console()
    error_console = Console(stderr=True, style="bold red")

    if auto_connect and not os.environ.get("CIRUN_API_KEY"):
        error_console.print("Error: CIRUN_API_KEY environment variable is required for --auto-connect")
        raise typer.Exit(code=1)

    # Check if AWS CLI is installed
    try:
        subprocess.run(
            ["aws", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        error_console.print("Error: AWS CLI is not installed or not found in PATH")
        error_console.print("Install it from: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html")
        raise typer.Exit(code=1)

    # Check caller identity
    console.print("[bold blue]Checking AWS CLI configuration...[/bold blue]")
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--output", "json"],
            capture_output=True,
            check=True,
            text=True
        )
        caller_identity = json.loads(result.stdout)
    except subprocess.CalledProcessError:
        error_console.print("Error: Not authenticated with AWS CLI")
        error_console.print("Please run: aws configure")
        raise typer.Exit(code=1)

    # Display account details
    console.print("\n[bold green]AWS Account Details:[/bold green]")
    console.print(f"  Account ID: [bold]{caller_identity.get('Account', 'N/A')}[/bold]")
    console.print(f"  ARN:        [bold]{caller_identity.get('Arn', 'N/A')}[/bold]")
    console.print(f"  User ID:    [bold]{caller_identity.get('UserId', 'N/A')}[/bold]")
    console.print("")

    # Generate IAM user name if not provided
    if not name:
        from datetime import datetime, timezone
        name = f"cirun-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    # Confirm before creating
    typer.confirm(
        f"Create IAM user '{name}' with policy '{policy_arn}'?",
        abort=True,
    )

    # Create IAM user
    console.print(f"[bold blue]Creating IAM user '[bold green]{name}[/bold green]'...[/bold blue]")
    try:
        subprocess.run(
            ["aws", "iam", "create-user", "--user-name", name],
            capture_output=True,
            check=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        error_console.print(f"Error creating IAM user: {e.stderr}")
        raise typer.Exit(code=1)

    # Attach policy
    console.print(f"[bold blue]Attaching policy [bold green]{policy_arn}[/bold green]...[/bold blue]")
    try:
        subprocess.run(
            [
                "aws", "iam", "attach-user-policy",
                "--user-name", name,
                "--policy-arn", policy_arn,
            ],
            capture_output=True,
            check=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        error_console.print(f"Error attaching policy: {e.stderr}")
        raise typer.Exit(code=1)

    # Create access key
    console.print("[bold blue]Creating access key...[/bold blue]")
    try:
        result = subprocess.run(
            ["aws", "iam", "create-access-key", "--user-name", name, "--output", "json"],
            capture_output=True,
            check=True,
            text=True
        )
        key_data = json.loads(result.stdout).get("AccessKey", {})
    except subprocess.CalledProcessError as e:
        error_console.print(f"Error creating access key: {e.stderr}")
        raise typer.Exit(code=1)

    access_key = key_data.get("AccessKeyId")
    secret_key = key_data.get("SecretAccessKey")

    # Display credentials
    success_console = Console(style="bold green")
    success_console.rule("[bold green]")
    success_console.print("[bold green]✓[/bold green] IAM user created successfully!")
    success_console.print("")
    success_console.print("[bold yellow]AWS Credentials for Cirun:[/bold yellow]")
    success_console.print("")
    success_console.print(f"  AWS_ACCESS_KEY_ID:     [bold]{access_key}[/bold]")
    success_console.print(f"  AWS_SECRET_ACCESS_KEY: [bold]{secret_key}[/bold]")
    success_console.print("")
    success_console.print("[bold red]⚠️  Save the SECRET_ACCESS_KEY - it won't be shown again![/bold red]")
    success_console.rule("[bold green]")

    # Auto-connect if requested
    if auto_connect:
        console.print("\n[bold blue]Connecting credentials to Cirun...[/bold blue]")
        credentials = {
            "access_key": access_key,
            "secret_key": secret_key,
        }
        _connect_cloud(name="aws", credentials=credentials)


@cloud_create.command(name="gcp")
def create_gcp(
        name: str = typer.Option(
            None,
            "--name",
            help="Name for the service account (optional, auto-generated if not provided)"
        ),
        role: str = typer.Option(
            "roles/compute.admin",
            "--role",
            help="IAM role to grant the service account"
        ),
        auto_connect: bool = typer.Option(
            False,
            "--auto-connect",
            help="Automatically connect the created credentials to Cirun"
        ),
):
    """Create GCP Service Account credentials for Cirun"""
    import os
    import tempfile

    console = Console()
    error_console = Console(stderr=True, style="bold red")

    if auto_connect and not os.environ.get("CIRUN_API_KEY"):
        error_console.print("Error: CIRUN_API_KEY environment variable is required for --auto-connect")
        raise typer.Exit(code=1)

    # Check if gcloud CLI is installed
    try:
        subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        error_console.print("Error: gcloud CLI is not installed or not found in PATH")
        error_console.print("Install it from: https://cloud.google.com/sdk/docs/install")
        raise typer.Exit(code=1)

    # Get current project
    console.print("[bold blue]Checking gcloud CLI configuration...[/bold blue]")
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            check=True,
            text=True
        )
        project_id = result.stdout.strip()
    except subprocess.CalledProcessError:
        error_console.print("Error: No active GCP project configured")
        error_console.print("Please run: gcloud config set project PROJECT_ID")
        raise typer.Exit(code=1)

    if not project_id or project_id == "(unset)":
        error_console.print("Error: No active GCP project configured")
        error_console.print("Please run: gcloud config set project PROJECT_ID")
        raise typer.Exit(code=1)

    # Check authentication
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            capture_output=True,
            check=True,
            text=True
        )
        active_account = result.stdout.strip()
    except subprocess.CalledProcessError:
        active_account = None

    if not active_account:
        error_console.print("Error: Not logged in to gcloud CLI")
        error_console.print("Please run: gcloud auth login")
        raise typer.Exit(code=1)

    # Display account details
    console.print("\n[bold green]GCP Account Details:[/bold green]")
    console.print(f"  Account:    [bold]{active_account}[/bold]")
    console.print(f"  Project ID: [bold]{project_id}[/bold]")
    console.print("")

    # Generate service account name if not provided
    if not name:
        from datetime import datetime, timezone
        name = f"cirun-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    sa_email = f"{name}@{project_id}.iam.gserviceaccount.com"

    # Confirm before creating
    typer.confirm(
        f"Create service account '{name}' with {role} on project '{project_id}'?",
        abort=True,
    )

    # Create service account
    console.print(f"[bold blue]Creating service account '[bold green]{name}[/bold green]'...[/bold blue]")
    try:
        subprocess.run(
            [
                "gcloud", "iam", "service-accounts", "create", name,
                "--display-name", f"Cirun service account ({name})",
                "--project", project_id,
            ],
            capture_output=True,
            check=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        error_console.print(f"Error creating service account: {e.stderr}")
        raise typer.Exit(code=1)

    # Wait for service account to be available
    for _ in range(10):
        result = subprocess.run(
            ["gcloud", "iam", "service-accounts", "describe", sa_email,
             "--project", project_id],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            break
        time.sleep(2)
    else:
        error_console.print("Service account was not ready in time.")
        raise typer.Exit(code=1)

    # Grant IAM role
    console.print(f"[bold blue]Granting [bold green]{role}[/bold green] role...[/bold blue]")
    try:
        subprocess.run(
            [
                "gcloud", "projects", "add-iam-policy-binding", project_id,
                "--member", f"serviceAccount:{sa_email}",
                "--role", role,
                "--format", "json",
            ],
            capture_output=True,
            check=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        error_console.print(f"Error granting IAM role: {e.stderr}")
        raise typer.Exit(code=1)

    # Create key file
    console.print("[bold blue]Creating service account key...[/bold blue]")
    try:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            key_file_path = tmp.name

        subprocess.run(
            [
                "gcloud", "iam", "service-accounts", "keys", "create", key_file_path,
                "--iam-account", sa_email,
            ],
            capture_output=True,
            check=True,
            text=True
        )

        with open(key_file_path, "r") as f:
            credentials = json.loads(f.read())
    except subprocess.CalledProcessError as e:
        error_console.print(f"Error creating service account key: {e.stderr}")
        raise typer.Exit(code=1)
    finally:
        os.unlink(key_file_path)

    # Display credentials
    success_console = Console(style="bold green")
    success_console.rule("[bold green]")
    success_console.print("[bold green]✓[/bold green] Service account created successfully!")
    success_console.print("")
    success_console.print("[bold yellow]GCP Credentials for Cirun:[/bold yellow]")
    success_console.print("")
    success_console.print(f"  Project ID:      [bold]{credentials.get('project_id')}[/bold]")
    success_console.print(f"  Client Email:    [bold]{credentials.get('client_email')}[/bold]")
    success_console.print(f"  Client ID:       [bold]{credentials.get('client_id')}[/bold]")
    success_console.print(f"  Private Key ID:  [bold]{credentials.get('private_key_id')}[/bold]")
    success_console.print("")
    success_console.print("[bold red]⚠️  The private key cannot be recovered if lost![/bold red]")
    success_console.rule("[bold green]")

    # Auto-connect if requested
    if auto_connect:
        console.print("\n[bold blue]Connecting credentials to Cirun...[/bold blue]")
        _connect_cloud(name="gcp", credentials=credentials)


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
