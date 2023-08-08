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


class CondaDriver(Driver):

    def _check_availability(self):
        try:
            self.list_virtual_envs()
        except CommandNotFound as e:
            raise ImplementationNotFound(f"No implementation for {self.name} ; {str(e)}")

    def list_virtual_envs(self) -> List[str]:
        """A list of virtualenv names.

        Returns:
            A list of string names in case-sensitive alphanumeric order.

        Raises:
            CommandNotFound: If the required command could not be found.
        """
        return sorted(self._environment_names_and_paths().keys())

    def _environment_names_and_paths(self) -> dict[str, str]:
        list_virtual_envs_command = "conda info --envs"
        command = sub_shell_command(list_virtual_envs_command)
        logger.debug(f"Running command: {command}")
        status, output = get_status_output(command)
        if status == 0:
            return dict(line.split() for line in output.splitlines(keepends=False))
        logger.error(output)
        if status == 127:  # Pyenv is not installed
            raise CommandNotFound(f"{output}. Have you installed conda?")
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
        # Create a virtual environment with conda using a command like:
        #   conda create --name myenv python=3.6

        python_arg = f"python={python}" if python else ""
        #system_site_packages_arg = "--system-site-packages" if system_site_packages else ""
        #pip_arg = parse_package_arg("pip", pip)
        #setuptools_arg = parse_package_arg("setuptools", setuptools)
        #wheel_arg = parse_package_arg("wheel", wheel)

        args = " ".join(
            (
                python_arg,
                #system_site_packages_arg,
                #pip_arg,
                #setuptools_arg,
                #wheel_arg,
            )
        )

        # Create
        create_command = sub_shell_command(f"conda create --name {name} {args}")
        logger.info(create_command)
        status, output = get_status_output(create_command)

        if status != 0:
            raise RuntimeError(f"Could not create virtual environment: {name}")

        ENVIRONMENT_LOCATION_REGEX = re.compile(r"environment location: (.*)\n")
        m = ENVIRONMENT_LOCATION_REGEX.search(output)
        if m is not None:
            location = m.group(1)
            logger.debug(f"Found environment location: {location}")
            return Path(location)

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

        command = sub_shell_command(f"conda remove --name {name} --all")
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
        names_and_paths = self._environment_names_and_paths()
        if name not in names_and_paths:
            raise ValueError(
                f"No virtual environment called {name!r} is found. "
                f"Found {', '.join(map(repr, names_and_paths.keys()))}'"
            )
        return Path(names_and_paths[name])
