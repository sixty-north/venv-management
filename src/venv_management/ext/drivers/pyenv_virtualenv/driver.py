import logging
import subprocess
import sys

from venv_management.driver import Driver
from venv_management.errors import CommandNotFound, ImplementationNotFound
from venv_management.utilities import _sub_shell_command, _getstatusoutput

logger = logging.getLogger(__name__)

class PyEnvVirtualEnvDriver(Driver):


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
        lsvirtualenv_command = "pyenv virtualenvs"
        command = _sub_shell_command(lsvirtualenv_command)
        logger.debug(command)
        status, output = _getstatusoutput(command)
        if status == 0:
            # TODO: Parse these output lines
            return output.splitlines(keepends=False)
        logger.error(output)
        if status == 127:
            raise CommandNotFound(output)
        raise RuntimeError(output)

    def remove_virtual_env(self, name):
        """Remove a virtual environment.

        Args:
            name: The name of the virtual environment to remove.

        Raises:
            ValueError: If there is no environment with the given name.
            RuntimeError: If the virtualenv could not be removed.
        """
        if not name:
            # When provided with an empty string, rmvirtualenv removes all virtual environments (!)
            # https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/346/rmvirtualenv-removes-all-virtualenvs
            raise ValueError("The name passed to remove_virtual_env cannot be empty")
        command = _sub_shell_command(f"rmvirtualenv {name}")
        logger.debug("command = %r", command)
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding=sys.getdefaultencoding()
        )
        # rmvirtualenv returns success (0) even when it fails because no such environment exists
        # https://bitbucket.org/virtualenvwrapper/virtualenvwrapper/issues/283/some-commands-give-non-zero-exit-codes
        # but it does return a message on stderr
        stderr = process.stderr
        if len(stderr) != 0:
            raise ValueError(stderr)