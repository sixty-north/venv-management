import inspect
from abc import ABC, abstractmethod
from pathlib import Path

import pkg_resources
import stevedore
import stevedore.exception


class ExtensionError(Exception):
    pass


def create_extension(kind, namespace, name, exception_type, *args, **kwargs):
    try:
        manager = stevedore.driver.DriverManager(
            namespace=namespace,
            name=name,
            invoke_on_load=True,
            invoke_args=args,
            invoke_kwds={**kwargs, "name": name},
        )
    except stevedore.exception.NoMatches as no_matches:
        names = list_extensions(namespace)
        name_list = ", ".join(names)
        raise exception_type(
            f"No {kind} matching {name !r}. Available {kind}s: {name_list}"
        ) from no_matches
    driver = manager.driver
    return driver


def list_extensions(namespace):
    """List the names of the extensions available in a given namespace."""
    extensions = stevedore.ExtensionManager(
        namespace=namespace,
        invoke_on_load=False,
    )
    return extensions.names()


def list_dirpaths(namespace):
    """A mapping of extension names to extension package paths."""
    extensions = stevedore.ExtensionManager(
        namespace=namespace,
        invoke_on_load=False,
    )
    return {name: _extension_dirpath(ext) for name, ext in extensions.items()}


def _extension_dirpath(ext: stevedore.extension.Extension) -> Path:
    """Get the directory path to an extension package.

    Args:
        ext: A stevedore.extension.Extension instance.

    Returns:
        A absolute Path to the package containing the extension.
    """
    return Path(pkg_resources.resource_filename(ext.module_name, ""))


class Extension(ABC):
    def __init__(self, name):
        self._name = name

    @property
    def kind(self):
        return self._kind()

    @abstractmethod
    def _kind(self):
        raise NotImplementedError

    @property
    def name(self):
        return self._name

    @classmethod
    def dirpath(cls):
        """The directory path to the extension package."""
        package_name = inspect.getmodule(cls).__package__
        return pkg_resources.resource_filename(package_name, "")

    @property
    def version(self):
        return "1.0.0"  # We allow extensions to have a distinct version but don't exploit this yet


