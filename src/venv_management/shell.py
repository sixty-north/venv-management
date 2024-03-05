import logging
import os
import subprocess
import sys
from os.path import expandvars, expanduser
from pathlib import Path
from shutil import which
from typing import List, Tuple

from venv_management.environment import preferred_shell, shell_is_interactive
from venv_management.utilities import str_to_bool

logger = logging.getLogger(__name__)


def sub_shell_command(command, suppress_setup_output=True):
    """Build a command to run a given command in an interactive subshell.

    Args:
        command: The command for the subshell.
        suppress_setup_output: Suppress output from the environment setup command if True,
            (the default), otherwise capture it.

    Returns:
        A string which can be used with the subprocess module.

    Raises:
        ValueError: If the subshell command could not be determined.
        RuntimeError: If the path to the shell could not be determined.
    """
    preferred_shell_name = os.environ.get("SHELL", "bash")
    logger.debug("preferred_shell_name from $SHELL = %r", preferred_shell_name)
    shell_name = preferred_shell(preferred_shell_name)
    logger.debug("shell_name = %r", shell_name)
    if "fish" in shell_name:
        logger.error("Support for fish not yet added")
        raise NotImplementedError("Support for fish not yet added")

    shell_filepath = which(shell_name)
    logger.debug("shell_filepath = %r", shell_filepath)
    if shell_filepath is None:
        raise RuntimeError(f"Could not determine the path to {shell_name}")
    shell_filepath = Path(shell_filepath)
    shell_filename = shell_filepath.name
    logger.debug("shell_filename = %r", shell_filename)
    rc_filename = f".{shell_filename}rc"
    logger.debug("rc_filename = %r", rc_filename)
    rc_filepath = Path.home() / rc_filename
    logger.debug("rc_filepath = %r", rc_filepath)
    interactive = shell_is_interactive()
    logger.debug("interactive = %s", interactive)
    commands = []
    use_setup = str_to_bool(expandvars(os.environ.get("VENV_MANAGEMENT_USE_SETUP", "yes")))
    setup_filepath_str = os.environ.get("VENV_MANAGEMENT_SETUP_FILEPATH", str(rc_filepath))
    setup_filepath = Path(expanduser(expandvars(setup_filepath_str)))
    if use_setup:
        redirection = " 1>/dev/null 2>&1" if suppress_setup_output else ""
        commands.append(f". {setup_filepath}{redirection}")
    if command:
        commands.append(command)

    logger.debug("setup_filepath = %s", setup_filepath)
    args = [
        str(shell_filepath),
        "-c",  # Run command
        *(["-i"] if interactive else []),
        " && ".join(commands),
    ]
    return args


def get_status_output(cmd: List[str], success_statuses=None) -> Tuple[int, str]:
    """    Return (status, output) of executing cmd in a shell.

    Args:
        cmd: A list of command arguments to be executed.
        success_statuses: A container of integer status codes which indicate success.

    Execute the string 'cmd' in a shell with 'check_output' and
    return a 2-tuple (status, output). Universal newlines mode is used,
    meaning that the result with be decoded to a string.

    A trailing newline is stripped from the output.
    The exit status for the command can be interpreted
    according to the rules for the function 'wait'.
    """
    if success_statuses is None:
        success_statuses = {0}
    logger.debug("command = %r", cmd)
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding=sys.getdefaultencoding()
    )
    status = process.returncode
    stderr = process.stderr
    stdout = process.stdout
    if status in success_statuses:
        data = stdout
        if data[-1:] == '\n':
            data = data[:-1]
    else:
        data = (f"STATUS: {status} ; \n"
                f"STDOUT: {stdout} ; \n"
                f"STDERR: {stderr}"
        )
    logger.debug("status = %d", status)
    logger.debug("data = %s", data)
    return status, data


def has_interactive_warning(line: str):
    """Determine whether a line of text contains a warning emitted by a shell.

    The shell program itself (e.g. bash) can emit warnings under certain circumstances
    which clutter output; for example, when running a shell in interactive mode without
    a connected terminal. This predicate can identify lines of text containing such
    warnings.

    Args:
        line: A string which may contain a shell warning.

    Returns:
        True if the line contains a shell warning, otherwise False.
    """
    return (
            "cannot set terminal process group" in line
            or "Inappropriate ioctl for device" in line
            or "no job control in this shell" in line
    )


def remove_interactive_shell_warnings(lines: str) -> str:
    """Remove shell warnings from lines of text.

    The shell program itself (e.g. bash) can emit warnings under certain circumstances
    which clutter output; for example, when running a shell in interactive mode without
    a connected terminal. This predicate can identify lines of text containing such
    warnings.

    Args:
        lines: A string (possibly multiline) which may contain lines which have shell warnings.

    Returns:
        The argument string without any lines containing matching shell warnings.
    """
    lines = lines.splitlines(keepends=True)
    lines = [line for line in lines if not has_interactive_warning(line)]
    lines = "".join(lines)
    return lines
