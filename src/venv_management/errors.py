"""Exception classes.
"""

class CommandNotFound(Exception):
    """Raised when a shell command could not be found."""


class ImplementationNotFound(Exception):
    "Raised when a virtual environment driver is not backed by a working implementation."


class PythonNotFound(Exception):
    "Raised when the requested Python version is not found."