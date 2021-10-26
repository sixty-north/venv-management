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
        self._check_availability()

    @abstractmethod
    def _check_availability(self):
        raise NotImplementedError

    @abstractmethod
    def list_virtual_envs(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def make_virtual_env(
            self,
            name,
            *,
            python=None,
            project_path=None,
            packages=None,
            requirements_file=None,
            system_site_packages=False,
            pip=True,
            setuptools=True,
            wheel=True,
    ):
        """Make a virtual env.

        Args:
            name: The name of the virtual environment.

            project_path: An optional path to a project which will be associated with the
                new virtual environment.

            packages: An optional sequence of package names for packages to be installed.

            requirements_file: An optional path to a requirements file to be installed.

            python: The target interpreter for which to create a virtual environment, either
                the name of the executable, or full path.

            system_site_packages: If True, give access to the system site packages.

            pip: If True, or 'latest' the latest pip will be installed. If False, pip will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

            setuptools: If True, or 'latest' the latest pip will be installed. If False, pip will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

            wheel: If True, or 'latest' the latest pip will be installed. If False, pip will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

        Returns:
            The Path to the root of the virtualenv, or None if the path could not be determined.

        Raises:
            CommandNotFound: If the the required command could not be found.
            RuntimeError: If the virtualenv could not be created.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_virtual_env(self, name):
        """Remove a virtual environment.

        Args:
            name: The name of the virtual environment to be removed.

        Raises:
            ValueError: If the name is empty.
        """
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
