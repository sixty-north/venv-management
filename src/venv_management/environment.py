import os
from os.path import expandvars

from venv_management.utilities import str_to_bool


def preferred_shell(preferred_shell_name):
    """The preferred shell from the VENV_MANAGEMENT_SHELL environment variable.

    Args:
        preferred_shell_name: The name of the preferred shell to use if the environment variable
            VENV_MANAGEMENT_SHELL is not set.

    Returns:
        The name of the preferred shell.
    """
    return expandvars(os.environ.get("VENV_MANAGEMENT_SHELL", preferred_shell_name))


def shell_is_interactive():
    """True if the shell has been set to interactive.

    Control the setting with the VENV_MANAGEMENT_INTERACTIVE_SHELL environment variable by
    setting it to 'yes' or 'no'.

    Returns:
        True if the shell is interactive, otherwise False.
    """
    return str_to_bool(expandvars(os.environ.get("VENV_MANAGEMENT_INTERACTIVE_SHELL", "no")))
