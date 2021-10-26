import uuid

from venv_management import make_virtual_env, list_virtual_envs, discard_virtual_env


def test_make_virtual_envs_with_one_env():
    name = "venv-management-{}".format(uuid.uuid4())
    make_virtual_env(name)
    try:
        envs = list_virtual_envs()
    finally:
        discard_virtual_env(name)
    assert name in envs
