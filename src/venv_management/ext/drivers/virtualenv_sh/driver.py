import logging

from venv_management.driver import Driver
from venv_management.errors import CommandNotFound, ImplementationNotFound
from venv_management.utilities import _sub_shell_command, _getstatusoutput

logger = logging.getLogger(__name__)

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

    def remove_virtual_env(self, name):
        if not name:
            raise ValueError("The name passed to remove_virtual_env cannot be empty")
        command = _sub_shell_command(f"rmvirtualenv {name}")
        logger.debug("command = %r", command)
        status, output = _getstatusoutput(command)
        if status == 0:
            return
        logger.debug(output)
        if status == 127:
            raise CommandNotFound(output)
        raise ValueError(output)