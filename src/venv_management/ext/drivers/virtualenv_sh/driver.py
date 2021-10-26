import logging
import re
from pathlib import Path

from venv_management.driver import Driver
from venv_management.errors import CommandNotFound, ImplementationNotFound
from venv_management.tools import _parse_package_arg
from venv_management.utilities import _sub_shell_command, _getstatusoutput

logger = logging.getLogger(__name__)


DESTINATION_PATTERN = r"dest=([^,]+)"
DESTINATION_REGEX = re.compile(DESTINATION_PATTERN)

class VirtualEnvShDriver(Driver):

    def _check_availability(self):
        try:
            self.list_virtual_envs()
        except CommandNotFound:
            raise ImplementationNotFound(f"No implementation for {self.name}")


    def list_virtual_envs(self) -> list[str]:
        """A list of virtualenv names.

        Returns:
            A list of string names in case-sensitive alphanumeric order.

        Raises:
            FileNotFoundError: If virtualenvwrapper.sh could not be located.
        """
        # Accommodate the fact that virtualenvwrapper is not disciplined about success/failure exit codes
        # https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/283/some-commands-give-non-zero-exit-codes
        lsvirtualenv_command = "lsvirtualenvs -b"
        command = _sub_shell_command(lsvirtualenv_command)
        logger.debug(command)
        status, output = _getstatusoutput(command)
        if status == 0:
            return output.splitlines(keepends=False)
        logger.debug(output)
        if status == 127:
            raise CommandNotFound(output)
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
        project_path_arg = f"-a {project_path}" if project_path else ""
        packages_args = [f"-i {package}" for package in packages] if packages else []
        requirements_arg = f"-r{requirements_file}" if requirements_file else ""
        python_arg = f"--python={python}" if python else ""
        system_site_packages_arg = "--system-site-packages" if system_site_packages else ""
        pip_arg = _parse_package_arg("pip", pip)
        setuptools_arg = _parse_package_arg("setuptools", setuptools)
        wheel_arg = _parse_package_arg("wheel", wheel)

        args = " ".join(
            (
                project_path_arg,
                *packages_args,
                requirements_arg,
                python_arg,
                system_site_packages_arg,
                pip_arg,
                setuptools_arg,
                wheel_arg,
            )
        )

        command = _sub_shell_command(f"mkvirtualenv {name} {args}")
        logger.info(command)
        # Accommodate the fact that virtualenvwrapper is not disciplined about success/failure exit codes
        # https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/283/some-commands-give-non-zero-exit-codes
        status, output = _getstatusoutput(command)
        if status == 127:
            raise CommandNotFound(output)
        if status != 0:
            raise RuntimeError(f"Could not run {command}")
        lines = output.splitlines(keepends=False)
        for line in lines:
            logger.debug("line = %s", line)
            m = DESTINATION_REGEX.search(line)
            if m is not None:
                dest = m.group(1)
                logger.debug("Found dest = %s", dest)
                return Path(dest)
        message = "Could not find dest for virtualenv {name!r}"
        logger.warning(message)
        raise RuntimeError(message)

    def remove_virtual_env(self, name):
        if not name:
            raise ValueError("The name passed to remove_virtual_env cannot be empty")
        if name not in self.list_virtual_envs():
            raise ValueError(f"No virtual environment called {name!r} to remove")
        command = _sub_shell_command(f"rmvirtualenv {name}")
        logger.debug("command = %r", command)
        status, output = _getstatusoutput(command)
        if status == 0:
            if name in self.list_virtual_envs():
                raise RuntimeError(f"Failed to remove virtual environment {name!r}")
            return
        logger.debug(output)
        if status == 127:
            raise CommandNotFound(output)
