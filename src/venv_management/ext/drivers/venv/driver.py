import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

from venv_management import PythonNotFound
from venv_management.driver import Driver

logger = logging.getLogger(__name__)

DEFAULT_VENVS_DIRPATH = Path.home() / ".virtualenvs"


class VEnvDriver(Driver):
    """A driver using the Python Standard Library venv module.

    This driver expects manages virtual environments in either the directory pointed to by $WORKON_HOME
    or, if the former is not defined, $HOME/.virtualenvs. If necessary, the virtual environment directory
    will be created.
    """
    def __init__(self, name: str):
        super().__init__(name)
        workon_home_dirpath = os.environ.get("WORKON_HOME")
        self._venvs_dirpath = Path(
            os.path.expandvars(workon_home_dirpath)
            if workon_home_dirpath else
            DEFAULT_VENVS_DIRPATH
        ).expanduser()

    def _check_availability(self):
        import venv
        self._venv_module = venv

    def list_virtual_envs(self) -> List[str]:
        if not self._venvs_dirpath.is_dir():
            if self._venvs_dirpath.exists():
                raise RuntimeError(f"The virtual environment directory {self._venvs_dirpath} is not a directory")
            return []
        return [
            subdir.name
            for subdir in self._venvs_dirpath.iterdir()
            if subdir.is_dir() and (subdir / "pyvenv.cfg").is_file()
        ]

    def make_virtual_env(self, name, *, python=None, project_path=None, packages=None, requirements_file=None,
                         system_site_packages=False, pip=True, setuptools=True, wheel=True) -> Optional[Path]:
        if not self._venvs_dirpath.is_dir():
            if self._venvs_dirpath.exists():
                raise RuntimeError(f"The virtual environment directory {self._venvs_dirpath} is not a directory")
            self._venvs_dirpath.mkdir(parents=True, exist_ok=True)

        virtualenv_dirpath = self._venvs_dirpath / name

        if python:
            python_exe = Path(python)
            if not python_exe.is_file():
                if (found := shutil.which(python)) is not None:
                    python_exe = Path(found)
        else:
            python_exe = Path(sys.executable)

        if not python_exe.is_file():
            raise PythonNotFound(f"Could not locate Python {python}")

        command = [python_exe, "-m", "venv", virtualenv_dirpath]

        if system_site_packages:
            command.append("--system-site-packages")

        if not pip:
            command.append("--without-pip")

        if pip:
            command.append("--upgrade-deps")

        if project_path is not None:
            raise ValueError(f"Project path not supported for {self.name!r} driver")

        # TODO: setuptools, wheel, requirements_file, packages

        subprocess.run(command, check=True)
        return virtualenv_dirpath

    def remove_virtual_env(self, name: str):
        path = self.resolve_virtual_env(name)
        shutil.rmtree(path)

    def resolve_virtual_env(self, name: str) -> Path:
        if not name:
            raise ValueError("The name passed to resolve_virtual_env cannot be empty")
        if name not in self.list_virtual_envs():
            raise ValueError(f"No virtual environment called {name!r}")
        return self._venvs_dirpath / name
