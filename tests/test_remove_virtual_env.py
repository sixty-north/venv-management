import uuid

from _pytest.python_api import raises

from venv_management import remove_virtual_env


def test_remove_virtual_env_with_empty_name_raises_value_error():
    with raises(ValueError):
        remove_virtual_env("")


def test_remove_virtual_env_with_non_existent_name():
    name = "venv-management-{}".format(uuid.uuid4())
    with raises(ValueError):
        remove_virtual_env(name)
