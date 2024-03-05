import configparser
from pathlib import Path
from typing import Union


def pyvenv_config(env_dirpath: Path, key: str) -> Union[str, None]:
    """Read a value from a pyvenv config file.

    Args:
        env_dirpath: Path to the directory containing the pyvenv.cfg file.
        key: The key from which to lookup the associated value.

    Returns:
        The value from the pyvenv.cfg file, or None if the key does not exist
        in the pyvenv.cfg file or if the pyenv.cfg config file does not exist.
    """
    pyenv_cfg_path = env_dirpath / "pyvenv.cfg"
    value = None
    if pyenv_cfg_path.is_file():
        config_text = pyenv_cfg_path.read_text()
        config = configparser.ConfigParser()
        config.read_string("[root]\n" + config_text)

        try:
            config_executable = config["root"][key]
        except KeyError:
            pass
        else:
            value = config_executable.strip()
    return value
