import os

import requests

from cirun.utils import print_success_json, _print_error, _print_error_data

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
                raise ValueError(msg)

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def _get(self, path, *args, **kwargs):
        return requests.get(f"{self.api_endpoint}/{path}", headers=self._headers(), *args, **kwargs)

    def _post(self, path, *args, **kwargs):
        return requests.post(f"{self.api_endpoint}/{path}", headers=self._headers(), *args, **kwargs)

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
            install_github_app=None,
            print_error=False,
            installation_id=None
    ):
        """Activate repository for Cirun"""
        data = {
            "repository": name,
            "active": active
        }
        if install_github_app:
            self.install_github_app(name, installation_id)
        response = self._post("repo", json=data)
        if response.status_code not in [200, 201]:
            if print_error:
                _print_error(response)
            return response.json()
        return response.json()

    def _get_github_repo_id(self, owner, repo):
        url = f"{GITHUB_API}/repos/{owner}/{repo}"
        response = requests.get(url)
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
        print_success_json(response)
        return response

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
