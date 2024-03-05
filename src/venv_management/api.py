"""The public API.
"""
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
import logging
from typing import Optional, Union

from venv_management.driver import driver
from venv_management.pyenv_config import pyvenv_config
from venv_management.utilities import compatible_versions

logger = logging.getLogger(__file__)


def list_virtual_envs() -> list[str]:
    """A list of virtualenv names.

    Returns:
        A list of string names in case-sensitive alphanumeric order.

    Raises:
        ImplementationNotFound: If no virtualenvwrapper implementation could be found.
    """
    return driver().list_virtual_envs()


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
) -> Optional[Path]:
    """Make a virtual env.

    Args:
        name: The name of the virtual environment.

        python: The target interpreter for which to create a virtual environment, either
            the name of the executable, or full path.

        project_path: An optional path to a project which will be associated with the
            new virtual environment.

        packages: An optional sequence of package names for packages to be installed.

        requirements_file: An optional path to a requirements file to be installed.

        system_site_packages: If True, give access to the system site packages.

        pip: If True, or 'latest' the latest pip will be installed. If False, pip will not
            be installed. If 'bundled', the bundled version will be installed. If a specific
            version string is given, that version will be installed.

        setuptools: If True, or 'latest' the latest pip will be installed. If False, setuptools will
            not be installed. If 'bundled', the bundled version will be installed. If a specific
            version string is given, that version will be installed.

        wheel: If True, or 'latest' the latest pip will be installed. If False, wheel will not
            be installed. If 'bundled', the bundled version will be installed. If a specific
            version string is given, that version will be installed.

    Returns:
        The Path to the root of the virtualenv, or None if the path could not be determined.

    Raises:
        RuntimeError: If the virtualenv could not be created.
    """
    return driver().make_virtual_env(
        name,
        python=python,
        project_path=project_path,
        packages=packages,
        requirements_file=requirements_file,
        system_site_packages=system_site_packages,
        pip=pip,
        setuptools=setuptools,
        wheel=wheel
    )


def resolve_virtual_env(name) -> Path:
    """Given the name of a virtual environment, get its path.

    Args:
        The name of a virtual environment.

    Returns:
        The path to the virtual environment directory.

    Raises:
        ValueError: If the virtual environment name is not known.
        RuntimeError: If the path could not be determined.
    """
    return driver().resolve_virtual_env(name)


@contextmanager
def virtual_env(name, expected_version=None, *, force=False, **kwargs):
    """A context manager that ensures a virtualenv with the given name and version exists.

    Irrespective of whether the virtual environment already exists, it will be removed when the context manager exits.

    Args:
        name: The name of the environment to check for.

        expected_version: An optional required version as a string. "3.8" will match "3.8.2"

        force: Force replacement of an existing virtual environment which has the wrong version.

        **kwargs: Arguments which will be forwarded to mkvirtualenv if the environment
            needs to be created.

    Returns:
        A context manager that manages the lifecycle of the virtual environment.

    Raises:
        RuntimeError: If the virtual environment couldn't be created or replaced.
    """
    venv_path = ensure_virtual_env(name, expected_version, force=force, **kwargs)
    try:
        yield venv_path
    finally:
        remove_virtual_env(name)


def ensure_virtual_env(name, expected_version=None, *, force=False, **kwargs) -> Optional[Path]:
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
            not compatible_versions(actual_version, expected_version)
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


def remove_virtual_env(name: str):
    """Remove a virtual environment.

    Args:
        name: The name of the virtual environment to remove.

    Raises:
        ValueError: If there is no environment with the given name.
        RuntimeError: If the virtualenv could not be removed.
    """
    return driver().remove_virtual_env(name)


def discard_virtual_env(name: str):
    """Discard a virtual environment.

    Args:
        name: The name of the virtual environment to remove.

    Raises:
        RuntimeError: If the virtualenv could not be removed.
        ValueError: If the name is empty.
    """
    if not name:
        raise ValueError("The name passed to remove_virtual_env cannot be empty")
    try:
        remove_virtual_env(name)
    except ValueError:
        pass


def python_executable_path(env_dirpath: Union[Path, str]) -> Path:
    """Find the Python executable for a virtual environment.

    Args:
        env_dirpath: The path to the root of a virtual environment (Path or str).

    Returns:
        A Path object to the executable.

    Raises:
        ValueError: If the env_dirpath is not a virtual environment.
    """
    env_dirpath = Path(env_dirpath)
    exe_filepath = pyvenv_config(env_dirpath, "executable")

    if not exe_filepath:
        exe_filepath = (
            env_dirpath / "Scripts" / "python.exe"
            if sys.platform == "win32" else
            env_dirpath / "bin" / "python"
        )
    exe_filepath = Path(exe_filepath)

    if not exe_filepath.exists():
        raise ValueError(
            f"Could not locate Python executable for supposed virtual environment {env_dirpath}"
        )
    return exe_filepath


def python_name(env_dirpath: Union[Path, str]) -> str:
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


def python_version(env_dirpath: Union[Path, str]) -> str:
    """Find the version of the Python in virtual environment.

    Args:
        env_dirpath: The path to the root of a virtual environment (Path or str).

    Returns:
        A version string, such as "3.8.1"

    Raises:
        ValueError: If the env_dirpath is not a virtual environment.
    """
    env_dirpath = Path(env_dirpath)
    version = pyvenv_config(env_dirpath, "version")
    if not version:
        name = python_name(env_dirpath)
        version = name.split()[-1]
    return version


def driver_name() -> str:
    """Get the name of the driver."""
    return driver().name
