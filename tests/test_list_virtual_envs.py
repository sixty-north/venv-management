from venv_management import list_virtual_envs


def test_list_virtual_envs():
    envs = list_virtual_envs()
    print(envs)

