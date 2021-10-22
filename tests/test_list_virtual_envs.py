import uuid

from venv_management import list_virtual_envs, make_virtual_env, discard_virtual_env


def test_list_virtual_envs_with_no_envs():
    envs = list_virtual_envs()
    assert envs == []



def test_list_virtual_envs_with_one_env():
    name = "venv-management-{}".format(uuid.uuid4())
    make_virtual_env(name)
    try:
        envs = list_virtual_envs()
    finally:
        discard_virtual_env(name)
    assert name in envs
