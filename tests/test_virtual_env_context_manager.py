import uuid

from venv_management import virtual_env, list_virtual_envs


def test_virtual_env_context_manager():
    name = "venv-management-{}".format(uuid.uuid4())
    absent_before = name not in list_virtual_envs()
    with virtual_env(name):
        present_during = name in list_virtual_envs()
    absent_after = name not in list_virtual_envs()
    assert absent_before and present_during and absent_after

