from abc import abstractmethod

from venv_management.errors import ImplementationNotFound
from venv_management.extension import Extension, ExtensionError, create_extension, list_extensions

KIND = "driver"

DRIVER_NAMESPACE = f"venv_management.{KIND}"


class Driver(Extension):

    def _kind(self):
        return KIND

    def __init__(self, name):
        super().__init__(name)

    @staticmethod
    @abstractmethod
    def list_virtual_envs() -> list[str]:
        raise NotImplementedError


class DriverExtensionError(ExtensionError):
    pass


def create_driver(driver_name) -> Driver:
    """Create a driver

    Args:
        driver_name: The name of the driver to create.

    Returns:
        A Driver instance.

    Raises:
        ImplementationNotFoundError: If a driver could be created but the driver could not find
            a working virtualenvwrapper (or equivalent) implementation.
    """
    driver = create_extension(
        kind=KIND,
        namespace=DRIVER_NAMESPACE,
        name=driver_name,
        exception_type=DriverExtensionError,
    )
    return driver


def driver_names() -> list[Driver]:
    return list_extensions(DRIVER_NAMESPACE)

_driver = None

def driver():
    global _driver
    if _driver is None:
        for driver_name in driver_names():
            try:
                d = create_driver(driver_name)
            except ImplementationNotFound:
                pass
            else:
                _driver = d
                break
        else:  # no-break
            raise ImplementationNotFound("No suitable virtualenvwrapper installation found")
    return _driver
