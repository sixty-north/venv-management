"""Functions for wrapping virtualenv wrapper.
"""
import os
import re
import subprocess
from pathlib import Path
import logging


logger = logging.getLogger(__file__)


SUB_SHELLS_TEMPLATES = {
    "bash": "{shell_path} -c 'source ~/.bash_profile && {command}'",
    "zsh": "{shell_path} -c 'source ~/.zshrc && {command}'",
}


def _sub_shell_command(command):
    """Build a command to run a given command in a subshell.

    Args:
        command: The command for the subshell.

    Returns:
        A string which can be used with the subprocess module.

    Raises:
        ValueError: If the subshell command could not be determined.
    """
    shell_path = os.environ.get("SHELL", "/bin/sh")
    shell = os.path.basename(shell_path)
    try:
        template = SUB_SHELLS_TEMPLATES[shell]
    except KeyError:
        raise ValueError("Don't know how to initialize {shell}")
    command = template.format(shell_path=shell_path, command=command)
    return command


def list_virtual_envs():
    """A list of virtualenv names.

    Returns:
        A list of string names in case-sensitive alphanumeric order.

    Raises:
        FileNotFoundError: If virtualenvwrapper.sh could not be located.
    """
    command = _sub_shell_command("lsvirtualenv -b")
    logger.info(command)
    status, output = subprocess.getstatusoutput(command)
    # proc = subprocess.Popen(["/bin/zsh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    # stdout, stderr = proc.communicate(b'source ~/.zshrc && lsvirtualenv -b\n')
    # print(stdout)
    # print(stderr)
    if status != 0:
        raise RuntimeError(f"Could not run {command}")
    return output.splitlines(keepends=False)


DESTINATION_PATTERN = r"dest=([^,]+)"
DESTINATION_REGEX = re.compile(DESTINATION_PATTERN)


def make_virtual_env(
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
    status, output = subprocess.getstatusoutput(command)
    if status != 0:
        raise RuntimeError(f"Could not run {command}")
    lines = output.splitlines(keepends=False)
    for line in lines:
        m = DESTINATION_REGEX.search(line)
        if m is not None:
            return Path(m.group(1))
    return None


def resolve_virtual_env(name):
    """Given the name of a virtual environment, get its path.

    Args:
        The name of a virtual environment.

    Returns:
        The path to the virtual environment directory.

    Raises:
        ValueError: If the virtual environment name is not known.
        RuntimeError: If the path could not be determined.
    """
    if name not in list_virtual_envs():
        raise ValueError(f"Unknown virtual environment {name!r}")
    return virtual_envs_dirpath() / name


def virtual_envs_dirpath():
    """The directory in which new virtual environments are created.

    Returns:
        A path object.
    """
    return Path(os.path.expanduser(os.environ.get("WORKON_HOME", "~/.virtualenvs")))


def ensure_virtual_env(name, expected_version=None, *, force=False, **kwargs):
    """Ensure a virtualenv with the given name and version exists.

    Args:
        name: The name of the environment to check for.

        expected_version: An optional required version as a string. "3.8" will match "3.8.2"

        force: Force replacement of an existing virtual environment which has the wrong version.

        **kwargs: Arguments which will be forwarded to mkvirtualenv if the environment
            needs to be created.

    Returns:
        The path to the virtual environment.

    Raises:
        RuntimeError: If the virtual environment couldn't be created or replaced.
    """
    python_arg = f"python{expected_version}" if (expected_version is not None) else None
    try:
        env_dirpath = resolve_virtual_env(name)
    except ValueError:
        # No such virtual environment, so make it
        env_dirpath = make_virtual_env(name, python=python_arg, **kwargs)
    else:
        # An environment with the right name exists. Does it have the right version?
        actual_version = python_version(env_dirpath)
        if (expected_version is not None) and (
            not _compatible_versions(actual_version, expected_version)
        ):
            message = (
                f"Virtual environment at {env_dirpath} has actual version {actual_version}, "
                f"not expected version {expected_version}"
            )
            logger.warning(message)
            if force:
                remove_virtual_env(name)
                env_dirpath = make_virtual_env(name, python=python_arg, **kwargs)
            else:
                raise RuntimeError(message)
    return env_dirpath


def _compatible_versions(actual_version, expected_version):
    return all(
        actual == expected
        for actual, expected in zip(actual_version.split("."), expected_version.split("."))
    )


def remove_virtual_env(name):
    """Remove a virtual environment.

    Args:
        name: The name of the virtual environment to remove.

    Raises:
        ValueError: If there is no environment with the given name.
        RuntimeError: If the virtualenv could not be removed.
    """
    command = _sub_shell_command(f"rmvirtualenv {name}")
    logger.info(command)
    status, output = subprocess.getstatusoutput(command)
    if status != 0:
        raise RuntimeError(f"Could not run {command}")
    if "Did not find environment" in output:
        raise ValueError(output.splitlines(keepends=False)[1])


def discard_virtual_env(name):
    """Discard a virtual environment.

    Args:
        name: The name of the virtual environment to remove.

    Raises:
        RuntimeError: If the virtualenv could not be removed.
    """
    try:
        remove_virtual_env(name)
    except ValueError:
        pass


def python_executable_path(env_dirpath):
    """Find the Python executable for a virtual environment.

    Args:
        env_dirpath: The path to the root of a virtual environment (Path or str).

    Returns:
        A Path object to the executable.

    Raises:
        ValueError: If the env_dirpath is not a virtual environment.
    """
    dirpath = Path(env_dirpath)
    exe_filepath = dirpath / "bin" / "python"
    if not exe_filepath.exists():
        raise ValueError(
            f"Could not locate Python executable for supposed virtual environment {env_dirpath}"
        )
    return exe_filepath


def python_name(env_dirpath):
    """Find the name of the Python in a virtual environment.

    Args:
        env_dirpath: The path to the root of a virtual environment (Path or str).

    Returns:
        A descriptive string.

    Raises:
        ValueError: If the env_dirpath is not a virtual environment.
    """
    exe = python_executable_path(env_dirpath)
    command = f"{exe} --version"
    status, output = subprocess.getstatusoutput(command)
    if status != 0:
        raise RuntimeError(f"Could not run {command}")
    return output.splitlines(keepends=False)[0]


def python_version(env_dirpath):
    """Find the version of the Python in virtual environment.

    Args:
        env_dirpath: The path to the root of a virtual environment (Path or str).

    Returns:
        A version string, such as "3.8.1"

    Raises:
        ValueError: If the env_dirpath is not a virtual environment.
    """
    name = python_name(env_dirpath)
    version = name.split()[-1]
    return version


def _parse_package_arg(name, arg):
    if arg == True:
        option = ""
    elif arg == False:
        option = f"--no-{name}"
    else:
        option = f"--{name}={arg}"
    return option


# Aliases for the main functions with the same name as the
# virtualenvwrapper shell commands
lsvirtualenv = list_virtual_envs
mkvirtualenv = make_virtual_env
rmvirtualenv = remove_virtual_env
