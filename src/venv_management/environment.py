import os
from itertools import chain
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


def preferred_drivers(available_driver_names):
    """The preferred drivers.

    The preferred drivers are controlled by the VENV_MANAGEMENT_PREFERRED_DRIVERS and VENV_MANAGEMENT_EXCLUDE_DRIVERS
    environment variables, each of which can include a comma-separated list of driver names.

    Args:
        available_driver_names: A list of available driver names.

    Returns:
        A list of available driver names, with the preferred drivers first.
    """
    preferred_driver_names = expandvars(os.environ.get("VENV_MANAGEMENT_PREFERRED_DRIVERS", "")).split(",")
    excluded_driver_names = expandvars(os.environ.get("VENV_MANAGEMENT_EXCLUDED_DRIVERS", "")).split(",")
    names = list(
        driver for driver in
        chain(
            [driver_name for driver_name in preferred_driver_names if driver_name in available_driver_names],
            [driver_name for driver_name in available_driver_names if driver_name not in preferred_driver_names],
        )
        if driver not in excluded_driver_names
    )

    # The "venv" driver should always work, so if no preference was expressed, and if it's available, try it last
    # so that more 'sophisticated' implementations get an opportunity.
    if len(preferred_driver_names) == 0 and "venv" in names:
        names.remove("venv")
        names.append("venv")
    return names
