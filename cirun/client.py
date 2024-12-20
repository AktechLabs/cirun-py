import os

import requests

from cirun.utils import _print_error, _print_error_data

API_ENDPOINT = "https://api.cirun.io/api/v1"
GITHUB_API = "https://api.github.com"
GH_TOKEN_ENV_VAR = "GITHUB_TOKEN"


class CirunAPIException(Exception):
    pass


class Cirun:
    """Cirun Client to interact to cirun's API"""
    def __init__(self, token=None):
        """
        :param token: cirun's API client token
        """
        self.token = token
        self._get_credentials()
        self.api_endpoint = os.environ.get('CIRUN_API_ENDPOINT', API_ENDPOINT)

    def _get_credentials(self):
        if not self.token:
            try:
                token = os.environ['CIRUN_API_KEY']
                self.token = token
            except KeyError:
                msg = "Could not find CIRUN_API_KEY in environment variables"
                _print_error_data(msg)
                raise KeyError(msg)

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def _get(self, path, *args, **kwargs):
        return requests.get(f"{self.api_endpoint}/{path}", headers=self._headers(), *args, **kwargs)

    def _post(self, path, *args, **kwargs):
        return requests.post(f"{self.api_endpoint}/{path}", headers=self._headers(), *args, **kwargs)

    def _put(self, path, *args, **kwargs):
        return requests.put(f"{self.api_endpoint}/{path}", headers=self._headers(), *args, **kwargs)

    def get_repos(self, print_error=False):
        """Get all the repositories connected to cirun."""
        response = self._get("repo")
        if response.status_code not in [200, 201]:
            if print_error:
                return _print_error(response)
        return response.json()

    def set_repo(
            self,
            name,
            active=True,
            print_error=False,
            installation_id=None
    ):
        """
        Activate or deactivate a repository for Cirun.

        This method allows you to enable or disable a repository's integration with Cirun.
        When activating a repository, it can also handle the installation of the Cirun
        GitHub App if an `installation_id` is provided and `GITHUB_TOKEN` environment
        variable is set.

        Parameters
        ----------
        name: str
            Repository name
        active: bool
            ``True`` to activate, ``False`` otherwise. Default is ``True``
        installation_id: int
            Cirun App's Installation ID for the Organization

        Returns
        -------
        dict
        """
        data = {
            "repository": name,
            "active": active
        }
        gh_response_json = {}
        if installation_id:
            gh_response_json = self.install_github_app(name, installation_id)
        response = self._post("repo", json=data)
        if response.status_code not in [200, 201]:
            if print_error:
                _print_error(response)
            response.raise_for_status()
        response = response.json()
        if gh_response_json:
            response = {
                **response,
                "github_installation": gh_response_json
            }
        return response

    def _get_github_repo_id(self, owner, repo):
        url = f"{GITHUB_API}/repos/{owner}/{repo}"
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
        return response_json["id"]

    def install_github_app(self, name, installation_id):
        owner, repo = name.split("/")
        repository_id = self._get_github_repo_id(owner=owner, repo=repo)
        url = f"{GITHUB_API}/user/installations/{installation_id}/repositories/{repository_id}"
        if not os.environ.get(GH_TOKEN_ENV_VAR):
            _print_error_data(f"ERROR: Environment variable: '{GH_TOKEN_ENV_VAR}'"
                              f" not found. Unable to install Cirun GitHub App on {name}")
            return
        gh_token = os.environ[GH_TOKEN_ENV_VAR]
        headers = {
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json",
        }
        response = requests.put(url, headers=headers)
        if response.status_code not in [204, 304]:
            _print_error(response)
            response.raise_for_status()
        response = {
            "message": f"GitHub Installation done",
            "status_code": response.status_code
        }
        return response

    def update_access_control(self, org, repository_resource_access):
        json = {
            "org": org,
            "repository_resource_access": repository_resource_access
        }
        response = self._put("access-control", json=json)
        if response.status_code not in [200, 201]:
            _print_error(response)
        response.raise_for_status()
        return response

    def get_access_control(self, org):
        response = self._get("access-control", json={"org": org})
        if response.status_code != 200:
            return
        return response.json()

    def _create_access_control_repo_resource_data(
            self, repo,
            resources,
            action="add",
            teams=None,
            roles=None,
            users=None,
            users_from_json=None,
            policy_args=None,
    ):
        repository_resource_access = {
            "repository": repo,
            "resources": resources,
            "action": action,
            "policy_args": policy_args
        }
        repository_resource_access = {
            **repository_resource_access,
            "teams": teams,
            "users": users,
            "roles": roles,
            "users_from_json": users_from_json,
        }
        return repository_resource_access

    def remove_repo_from_resources(self, org, repo, resources):
        """
        Creates a Pull request in the `<org>/.cirun` repository updating the `.access.yml`
        to revoke access to specified resources for a repository within an organization.

        Parameters
        ----------
        org: str
            GitHub Organization
        repo: str
            GitHub Repository
        resources: List[str]
            List of resources

        Returns
        -------
        requests.Response
        """
        repository_resource_access = self._create_access_control_repo_resource_data(
            repo, resources, action="remove",
        )
        return self.update_access_control(org, [repository_resource_access])

    def add_repo_to_resources(
            self,
            org,
            repo,
            resources,
            teams=None,
            roles=None,
            users=None,
            users_from_json=None,
            policy_args=None,
    ):
        """
        Creates a Pull request in the `<org>/.cirun` repository updating the `.access.yml`
        to grant access to specified resources for a repository within an organization,
        with constraints for teams, roles, users, users_from_json, policy_args.

        Parameters
        ----------
        org : str
            The GitHub organization name.
        repo : str
            The name of the repository to which resources are to be added.
        resources : list of str
            A list of resource identifiers to grant access to.
        teams : list of str, optional
            Teams to grant access to the resources.
        roles : list of str, optional
            Roles to grant access to the resource, i.e. users with specified roles
            will have access to the resources.
        users : list of str, optional
            Users to grant access to the resources.
        users_from_json : str, optional
            Users specified via a JSON URL
        policy_args : dict, optional
            Additional policy arguments, such as `{"pull_request": True}` to enforce
            specific policies on access.

        Returns
        -------
        requests.Response
            The response object from the API after attempting to add access.

        Raises
        ------
        CirunAPIException
            If the API call fails with an error status code.
        """
        repository_resource_access = self._create_access_control_repo_resource_data(
            repo, resources, action="add", teams=teams, roles=roles,
            users=users, users_from_json=users_from_json, policy_args=policy_args
        )
        return self.update_access_control(org, [repository_resource_access])

    def _get_repo_policy(self, access_yml, repo):
        for policy in access_yml["policies"]:
            if policy['repo'] == repo:
                return policy['id']

    def get_repo_resources(self, org, repo):
        """
        Retrieve the list of resources that a repository has access to within an organization.

        This method parses the access control configuration to determine which resources
        the specified repository is permitted to access based on its assigned policies.

        Parameters
        ----------
        org : str
            The GitHub organization name.
        repo : str
            The repository name whose accessible resources are to be retrieved.

        Returns
        -------
        list of str or None
            A list of resource identifiers that the repository has access to, or `None`
            if access control configuration is not found.

        Raises
        ------
        KeyError
            If the repository does not have an associated policy in the access control configuration.
        """
        access_control = self.get_access_control(org)
        if not access_control:
            return
        access_yml = access_control["access_yml"]
        policy_id = self._get_repo_policy(access_yml, repo)
        repo_resources = []
        for access_item in access_yml["access_control"]:
            if policy_id in access_item["policies"]:
                repo_resources.append(access_item["resource"])
        return repo_resources

    def clouds(self, print_error=False):
        """
        Retrieve all cloud providers connected to Cirun.

        This method fetches the list of cloud providers that have been integrated
        with Cirun (have credentials added to cirun).

        Parameters
        ----------
        print_error : bool, optional
            If set to True, errors encountered during the API call will be printed.
            Default is False.

        Returns
        -------
        dict
            A dictionary containing information about connected cloud providers.

        Raises
        ------
        CirunAPIException
            If the API call fails and `print_error` is False.
        """
        response = self._get("cloud-connect")
        if response.status_code not in [200, 201]:
            if print_error:
                return _print_error(response)
        return response.json()

    def cloud_connect(self, name, credentials, print_error=False):
        """
        Connect a new cloud provider to Cirun.

        This method integrates a specified cloud provider with Cirun by providing the
        necessary credentials. Once connected, the cloud provider can be used to create
        GitHub Actions runners.

        Parameters
        ----------
        name: str
            Name of cloud provider
        credentials: str
            Cloud Credentials

        Returns
        -------
        dict:
            Response json

        Raises
        ------
        CirunAPIException
            If the API call fails and `print_error` is False.
        """

        data = {
            "cloud": name,
            "credentials": credentials
        }
        response = self._post("cloud-connect", json=data)
        if response.status_code not in [200, 201]:
            if print_error:
                _print_error(response)
            return response.json()
        return response.json()
