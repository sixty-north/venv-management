import uuid

from _pytest.python_api import raises

from venv_management import discard_virtual_env, make_virtual_env, list_virtual_envs


def test_discard_virtual_env_with_empty_name_raises_value_error():
    with raises(ValueError):
        discard_virtual_env("")


def test_discard_virtual_env_with_non_existent_name():
    name = "venv-management-{}".format(uuid.uuid4())
    discard_virtual_env(name)


def test_make_then_discard_virtual_env():
    name = "venv-management-{}".format(uuid.uuid4())
    make_virtual_env(name)
    exists_before_discarding = name in list_virtual_envs()
    discard_virtual_env(name)
    gone_after_discarding = name not in list_virtual_envs()
    assert exists_before_discarding and gone_after_discarding
