"""Exception classes.
"""

class CommandNotFound(Exception):
    """Raised when a shell command could not be found."""


class ImplementationNotFound(Exception):
    "Raised when a Driver is not backed by a working virtualenvwrapper implementation."

