import os

import requests

from cirun.utils import _print_error, _print_error_data

API_ENDPOINT = "https://api.cirun.io/api/v1"
GITHUB_API = "https://api.github.com"
GH_TOKEN_ENV_VAR = "GITHUB_TOKEN"


class CirunAPIException(Exception):
    pass


class Cirun:
    def __init__(self, token=None):
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
        """Activate repository for Cirun"""
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
            return response.json()
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
            policy_args=None,
    ):
        repository_resource_access = {
            "repository": repo,
            "resources": resources,
            "action": action,
            "policy_args": policy_args
        }
        if teams:
            repository_resource_access = {
                **repository_resource_access,
                "teams": teams
            }
        return repository_resource_access

    def remove_repo_from_resources(self, org, repo, resources, teams=None, policy_args=None):
        """
        Removes the access to the resource for the repository.
        """
        repository_resource_access = self._create_access_control_repo_resource_data(
            repo, resources, action="remove", teams=teams, policy_args=policy_args
        )
        return self.update_access_control(org, [repository_resource_access])

    def add_repo_to_resources(self, org, repo, resources, teams=None, policy_args=None):
        repository_resource_access = self._create_access_control_repo_resource_data(
            repo, resources, action="add", teams=teams,  policy_args=policy_args
        )
        return self.update_access_control(org, [repository_resource_access])

    def _get_repo_policy(self, access_yml, repo):
        for policy in access_yml["policies"]:
            if policy['repo'] == repo:
                return policy['id']

    def get_repo_resources(self, org, repo):
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
        """Returns all the connected cloud"""
        response = self._get("cloud-connect")
        if response.status_code not in [200, 201]:
            if print_error:
                return _print_error(response)
        return response.json()

    def cloud_connect(self, name, credentials, print_error=False):
        """Connect a cloud provider to cirun"""
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
