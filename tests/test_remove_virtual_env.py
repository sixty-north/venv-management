import uuid

from _pytest.python_api import raises

from venv_management import remove_virtual_env, make_virtual_env, list_virtual_envs


def test_remove_virtual_env_with_empty_name_raises_value_error():
    with raises(ValueError):
        remove_virtual_env("")


def test_remove_virtual_env_with_non_existent_name():
    name = "venv-management-{}".format(uuid.uuid4())
    with raises(ValueError):
        remove_virtual_env(name)


def test_make_then_remove_virtual_env():
    name = "venv-management-{}".format(uuid.uuid4())
    make_virtual_env(name)
    exists_before_removal = name in list_virtual_envs()
    remove_virtual_env(name)
    gone_after_removal = name not in list_virtual_envs()
    assert exists_before_removal and gone_after_removal


