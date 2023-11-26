import os

import pytest
import requests

from cirun import Cirun

MSG_401 = "This API Key is expired or non-existent."


@pytest.fixture
def set_api_key():
    os.environ['CIRUN_API_KEY'] = "random-key"


def test_access_control_add_repo_to_resource_401(set_api_key):
    cirun = Cirun()
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        cirun.add_repo_to_resources(
            "cirun", "cirun-py",
            teams=["team1", "team2", "team3"],
            roles=["role1", "role2", "role3"],
            users=["user1", "user2", "user3"],
            users_from_json="https://cirun.io/users.json",
            resources=["cirun-runner-1"]

        )
    assert exc.value.response.status_code == 401
    assert exc.value.response.json() == {'message': MSG_401}


def test_access_control_remove_repo_from_resource_401(set_api_key):
    cirun = Cirun()
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        cirun.remove_repo_from_resources("cirun", "cirun-py", resources=["cirun-runner-1"])
    assert exc.value.response.status_code == 401
    assert exc.value.response.json() == {'message': MSG_401}


def test_get_repo_resources(set_api_key):
    cirun = Cirun()
    cirun.get_repo_resources(org="aktechlabs", repo="cirun-py")
