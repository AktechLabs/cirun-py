import os

import requests
from rich.console import Console

API_ENDPOINT = "https://cirun.io/api/v1"


class CirunAPIException(Exception):
    pass


def _print_error(response):
    error_console = Console(stderr=True, style="bold red")
    try:
        rjson = response.json()
    except requests.exceptions.JSONDecodeError:
        rjson = {
            "responseContent": response.content.decode()
        }
    error_console.rule("[bold red]")
    error_console.print(f"Error")
    error_console.print_json(data=rjson)
    error_console.log(f"Response Status Code: {response.status_code}")
    error_console.rule("[bold red]")
    return rjson


class Cirun:
    def __init__(self, token=None):
        self.token = token
        self._get_credentials()

    def _get_credentials(self):
        if not self.token:
            try:
                token = os.environ['CIRUN_API_KEY']
                self.token = token
            except KeyError:
                raise ValueError("Could not find CIRUN_API_KEY in environment variables")

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def _get(self, path, *args, **kwargs):
        return requests.get(f"{API_ENDPOINT}/{path}", headers=self._headers(), *args, **kwargs)

    def _post(self, path, *args, **kwargs):
        return requests.post(f"{API_ENDPOINT}/{path}", headers=self._headers(), *args, **kwargs)

    def get_repos(self, print_error=False):
        """Get all the repositories connected to cirun."""
        response = self._get("repo")
        if response.status_code not in [200, 201]:
            if print_error:
                return _print_error(response)
        return response.json()

    def set_repo(self, name, active=True, print_error=False):
        """Activate repository for Cirun"""
        data = {
            "repository": name,
            "active": active
        }
        response = self._post("repo", json=data)
        if response.status_code not in [200, 201]:
            if print_error:
                _print_error(response)
            return response.json()
        return response.json()

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
