import uuid

from venv_management import ensure_virtual_env, list_virtual_envs, discard_virtual_env


def test_ensure_virtual_env_creates_when_necessary():
    name = "venv-management-{}".format(uuid.uuid4())
    absent_before_creation = name not in list_virtual_envs()
    try:
        ensure_virtual_env(name)
        exists_after_creation = name in list_virtual_envs()
    finally:
        discard_virtual_env(name)
    assert absent_before_creation and exists_after_creation


def test_ensure_virtual_env_is_idempotent():
    name = "venv-management-{}".format(uuid.uuid4())
    try:
        env_path_a = ensure_virtual_env(name)
        env_path_b = ensure_virtual_env(name)
    finally:
        discard_virtual_env(name)
    assert env_path_a == env_path_b

