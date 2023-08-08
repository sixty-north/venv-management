"""Utility functions.
"""


def compatible_versions(actual_version: str, required_version: str) -> bool:
    """Determine whether two versions are equal.

    Only the dot separated elements in common are taken into account, so
    actual "3.7.4" compared with "3.7" will return True.

    Args:
        actual_version: A dot separated version.
        required_version: A dot separated version.

    Returns:
        True if the actual_version is compatible with the required_version,
        otherwise False.
    """
    return all(
        actual == expected
        for actual, expected in zip(actual_version.split("."), required_version.split("."))
    )


def parse_package_arg(name, arg):
    """Make a command-line argument string specifing whether and which verison of a package to install.

    Args:
        name: The name of the package.
        arg: True if the package is required, False if the package is not required,
            or a string containing a version number if a specific version of the package
            is required.

    Returns:
        A string which can be used as an argument to the virtualenv command.
    """
    if arg == True:
        option = ""
    elif arg == False:
        option = f"--no-{name}"
    else:
        option = f"--{name}={arg}"
    return option


def str_to_bool (val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    # Note this implementation was copied and renamed from the now deprecated distutils.util.strtobool
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))