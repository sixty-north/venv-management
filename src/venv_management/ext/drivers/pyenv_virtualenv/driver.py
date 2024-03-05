import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import List

from venv_management.driver import Driver
from venv_management.errors import ImplementationNotFound, CommandNotFound, PythonNotFound
from venv_management.utilities import parse_package_arg
from venv_management.shell import (
    sub_shell_command, get_status_output,
    remove_interactive_shell_warnings,
)
from venv_management.environment import shell_is_interactive

logger = logging.getLogger(__name__)


# A part of the error message when an invalid Python version is specified in the command line
NO_SUCH_PYTHON_PATTERN = r"is not installed in pyenv"
NO_SUCH_PYTHON_REGEX = re.compile(NO_SUCH_PYTHON_PATTERN)

DESTINATION_PATTERN = r"dest=([^,]+)"
DESTINATION_REGEX = re.compile(DESTINATION_PATTERN)


class PyEnvVirtualEnvDriver(Driver):

    def _check_availability(self):
        try:
            self.list_virtual_envs()
        except (CommandNotFound, RuntimeError) as e:
            raise ImplementationNotFound(f"No implementation for {self.name} ; {str(e)}")

    def list_virtual_envs(self) -> List[str]:
        """A list of virtualenv names.

        Returns:
            A list of string names in case-sensitive alphanumeric order.

        Raises:
            FileNotFoundError: If virtualenvwrapper.sh could not be located.
        """
        list_virtual_envs_command = "pyenv virtualenvs --bare"
        command = sub_shell_command(list_virtual_envs_command)
        logger.debug(f"Running command: {command}")
        status, output = get_status_output(command)
        if status == 0:
            return output.splitlines(keepends=False)
        logger.error(output)
        if status == 127:  # Pyenv is not installed
            raise CommandNotFound(f"{output}. Have you installed pyenv?")
        if status == 1:  # The subcommand passed to Pyenv is not recognized
            raise CommandNotFound(f"{output}. Have you installed pyenv-virtualenv?")
        raise RuntimeError(output)

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
                new virtual environment. (not supported by pyenv-virtualenv)

            packages: An optional sequence of package names for packages to be installed.
                 (not supported by pyenv-virtualenv)

            requirements_file: An optional path to a requirements file to be installed.
                (not supported by pyenv-virtualenv)

            python: The target interpreter for which to create a virtual environment, either
                the name of the executable, or full path.

            system_site_packages: If True, give access to the system site packages.

            pip: If True, or 'latest' the latest pip will be installed. If False, pip will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

            setuptools: If True, or 'latest' the latest setuptools will be installed.
                If False, setuptools will not be installed.
                If 'bundled', the bundled version will be installed.
                If a specific version string is given, that version will be installed.

            wheel: If True, or 'latest' the latest pip will be installed. If False, pip will not
                be installed. If 'bundled', the bundled version will be installed. If a specific
                version string is given, that version will be installed.

        Returns:
            The Path to the root of the virtualenv, or None if the path could not be determined.

        Raises:
            CommandNotFound: If the required command could not be found.
            RuntimeError: If the virtualenv could not be created.
        """
        python_arg = f"--python={python}" if python else ""
        system_site_packages_arg = "--system-site-packages" if system_site_packages else ""
        pip_arg = parse_package_arg("pip", pip)
        setuptools_arg = parse_package_arg("setuptools", setuptools)
        wheel_arg = parse_package_arg("wheel", wheel)

        args = " ".join(
            (
                python_arg,
                system_site_packages_arg,
                pip_arg,
                setuptools_arg,
                wheel_arg,
            )
        )

        # Create
        create_command = sub_shell_command(f"pyenv virtualenv {args} {name}")
        logger.info(create_command)
        status, output = get_status_output(create_command)
        m = NO_SUCH_PYTHON_REGEX.search(output)
        if m is not None:
            raise PythonNotFound(f"Could not locate Python {python} ; {m.group(0)}")

        # Get current Python version
        python_version_command = sub_shell_command("pyenv version-name")
        status, output = get_status_output(python_version_command)
        if status != 0:
            raise RuntimeError(f"Could not run {python_version_command}")
        python_version = output.strip()

        # Activate
        activate_command = sub_shell_command(f"pyenv activate {name}")
        status, output = get_status_output(activate_command)
        if status != 0:
            raise RuntimeError(f"Could not activate virtual environment: {name}")

        # Get the path to the virtual environment root
        get_path_command = sub_shell_command(f"pyenv prefix {name}")
        status, output = get_status_output(get_path_command)
        if status != 0:
            raise RuntimeError(f"Could not get path for virtual environment: {name}")
        if output:
            return Path(output)

        raise RuntimeError(f"Could not get path for virtual environment: {name}")

    def remove_virtual_env(self, name):
        """Remove a virtual environment.

        Args:
            name: The name of the virtual environment to remove.

        Raises:
            ValueError: If there is no environment with the given name.
            RuntimeError: If the virtualenv could not be removed.
        """
        if not name:
            raise ValueError("The name passed to remove_virtual_env cannot be empty")
        if name not in self.list_virtual_envs():
            raise ValueError(f"No virtualenv named {name}")

        command = sub_shell_command(f"pyenv uninstall -f {name}")
        logger.debug("command = %r", command)
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding=sys.getdefaultencoding()
        )
        stderr = process.stderr
        if shell_is_interactive():
            stderr = remove_interactive_shell_warnings(stderr)
        if len(stderr) != 0:
            raise ValueError(stderr)

    def resolve_virtual_env(self, name: str) -> Path:
        """Resolve the path to a virtual environment.

        Args:
            name: The name of the virtual environment.

        Returns:
            The path to the virtual environment in the $HOME/.pyenv/versions/<virtual_env_name> format.
        """
        if not name:
            raise ValueError("The name passed to resolve_virtual_env cannot be empty")
        names = self.list_virtual_envs()
        if name not in names:
            raise ValueError(
                f"No virtual environment called {name!r} is found. "
                f"Found {', '.join(map(repr, names))}'"
            )
        command = sub_shell_command(f"pyenv prefix {name}")
        logger.debug("command = %r", command)
        status, output = get_status_output(command)
        return Path(output)
