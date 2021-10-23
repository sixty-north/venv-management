import logging

from venv_management.driver import Driver
from venv_management.errors import CommandNotFound, ImplementationNotFound
from venv_management.utilities import _sub_shell_command, _getstatusoutput

logger = logging.getLogger(__name__)

class VirtualEnvShDriver(Driver):

    def __init__(self, name):
        super().__init__(name)
        # TODO: Check that virtualenv-sh is available
        try:
            self.list_virtual_envs()
        except CommandNotFound:
            raise ImplementationNotFound(f"No implementation for {name}")


    @staticmethod
    def list_virtual_envs() -> list[str]:
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
