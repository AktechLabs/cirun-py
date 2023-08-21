from cirun import Cirun

MSG_401 = "This API Key is expired or non-existent."


def test_access_control_add_repo_to_resource_401():
    cirun = Cirun()
    response = cirun.add_repo_to_resources("cirun", "cirun-py", resources=["cirun-runner-1"])
    assert response.status_code == 401
    assert response.json() == {"message": MSG_401}


def test_access_control_remove_repo_from_resource_401():
    cirun = Cirun()
    response = cirun.add_repo_to_resources("cirun", "cirun-py", resources=["cirun-runner-1"])
    assert response.status_code == 401
    assert response.json() == {"message": MSG_401}


def test_get_repo_resources():
    cirun = Cirun()
    cirun.get_repo_resources(org="aktechlabs", repo="cirun-py")
