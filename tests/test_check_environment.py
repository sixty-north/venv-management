from venv_management import list_virtual_envs, check_environment


def test_check_environment():
    status, output = check_environment()
    print(f"{status = }")
    print(f"{output = }")
