import uuid

from _pytest.python_api import raises

from venv_management import remove_virtual_env, make_virtual_env, list_virtual_envs, \
    resolve_virtual_env, discard_virtual_env


def test_resolve_virtual_env_with_empty_name_raises_value_error():
    with raises(ValueError):
        resolve_virtual_env("")


def test_resolve_virtual_env_with_non_existent_name_raises_value_error():
    name = "venv-management-{}".format(uuid.uuid4())
    with raises(ValueError):
        resolve_virtual_env(name)


def test_make_then_resolve_virtual_env():
    name = "venv-management-{}".format(uuid.uuid4())
    try:
        made_path = make_virtual_env(name)
        resolved_path = resolve_virtual_env(name)
    finally:
        discard_virtual_env(name)
    assert resolved_path == made_path



