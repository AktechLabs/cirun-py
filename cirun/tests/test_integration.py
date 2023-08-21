from cirun import Cirun

MSG_400 = ("User doesn't have admin permissions on the "
           "access repository or Cirun application is not installed.")


def test_access_control_add_repo_to_resource_400s():
    cirun = Cirun()
    response = cirun.add_repo_to_resources("cirun", "cirun-py", resources=["cirun-runner-1"])
    response.status_code = 400
    assert response.json() == {"message": MSG_400}


def test_access_control_remove_repo_from_resource_400():
    cirun = Cirun()
    response = cirun.add_repo_to_resources("cirun", "cirun-py", resources=["cirun-runner-1"])
    response.status_code = 400
    assert response.json() == {"message": MSG_400}


def test_get_repo_resources():
    cirun = Cirun()
    cirun.get_repo_resources(org="aktechlabs", repo="cirun-py")
