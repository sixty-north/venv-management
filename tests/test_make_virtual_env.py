import uuid

import pytest

from venv_management import make_virtual_env, list_virtual_envs, discard_virtual_env, PythonNotFound


def test_make_virtual_envs_with_one_env():
    name = "venv-management-{}".format(uuid.uuid4())
    make_virtual_env(name)
    try:
        envs = list_virtual_envs()
    finally:
        discard_virtual_env(name)
    assert name in envs


def test_make_virtual_env_with_non_existent_python():
    name = "venv-management-{}".format(uuid.uuid4())
    with pytest.raises(PythonNotFound):
        make_virtual_env(name, python="python2.13")
