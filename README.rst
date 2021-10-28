===============
Venv Management
===============

A Python package for programmatic creation and management of Python virtual environments.


.. image:: https://github.com/rob-smallshire/renard/workflows/CI/badge.svg?branch=master
     :target: https://github.com/sixty-north/venv-management/actions?workflow=CI
     :alt: CI Status

.. image:: https://readthedocs.org/projects/venv-management/badge/?version=latest
    :target: https://venv-management.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


This document gives an overview. For more detail see the `documentation <https://venv-management.readthedocs.io/en/latest/?badge=latest>`_.


Prerequisites
=============

A virtualenvwrapper installation must have been installed and be available in a shell and configured
at shell start-up in the appropriate ``rc`` file (*e.g.* ``.bashrc``, but the documentation for more
details and options). The following virtualenvwrapper implementations have been tested:

  * `virtualenvwrapper <https://pypi.org/project/virtualenvwrapper/>`_
  * `virtualenv-sh <https://pypi.org/project/virtualenv-sh/>`_

Possibly in future we will also support:

  * `pyenv-virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_
  * `pew <https://pypi.org/project/pew/>`_

.. inclusion-begin-installation-marker-do-not-remove

Installation
------------

Install from PyPI using ``pip``::

  $ pip install venv-management

.. inclusion-end-installation-marker-do-not-remove


Synopsis
--------

Use the Python functions exported by the ``venv_management`` package to create, enumerate,
interrogate, and destroy virtual environments::

  >>> make_virtual_env("myenv")
  >>> python_version(env_path)
  '3.10.0'
  >>> list_virtual_envs()
  ['myenv']
  >>> env_path = resolve_virtual_env("myenv")
  >>> env_path
  /home/user/.virtualenvs/myenv
  >>> remove_virtual_env("myenv")
  >>>

Refer to the documentation to see all available functions.

.. inclusion-begin-configuration-marker-do-not-remove

Shell selection
---------------

This ``venv-management`` package delegates most operations to one of the ``virtualenvwrapper`` or
equivalent tools, which are implemented using shell scripts and shell functions. In order to invoke
these scripts and functions successfully the shell environment mush have been correctly configured.
By default ``venv-management`` attempts to use the current user's preferred shell by examining the
``$SHELL`` environment variable. This can be overridden by setting the ``$VENV_MANAGEMENT_SHELL``
variable with a shell executable name or the path to a shell executable, for example::

  export VENV_MANAGEMENT_SHELL=zsh

If neither ``$SHELL`` nor ``$VENV_MANAGEMENT_SHELL`` are set, an attempt to use ``bash`` will be
made.


Shell configuration
-------------------

The selected shell must be configured to make the ``virtualenvwrapper`` commands available. By
default, ``venv-management`` will source the ``rc`` file corresponding to the selected shell, for
example ``.bashrc`` for ``bash``, ``.zshrc`` for ``zsh``, and so on, on the basis that
``virtualenvwrapper`` initialization is often performed from these files. If the ``rc`` file for
the selected shell can only be usefully sourced in an interactive shell, set
``VENV_MANAGEMENT_INTERACTIVE_SHELL`` to ``yes``::


  export VENV_MANAGEMENT_INTERACTIVE_SHELL=yes

Should you wish to specify a different file for shell configuration, provide its path in the
``VENV_MANAGEMENT_SETUP_FILEPATH`` environment variable. For example, since ``.bashrc`` may return
immediately in non-interactive shells, and only login shells source ``.profile`` on start-up,
you may want to set up virtualenvwrapper or an equivalent in in a separate file, in this example
called ``.venvwraprc``::

  # .venvwraprc
  source /usr/local/bin/virtualenvwrapper.sh

and then source this file in turn from, say, ``.bashrc``.

If the ``VENV_MANAGEMENT_USE_SETUP`` variable is set to ``yes``, the script whose filepath is
specified in the ``VENV_MANAGEMENT_SETUP_FILEPATH`` variable will be as necessary before executing
the commands run by this package::

  export VENV_MANAGEMENT_USE_SETUP=yes
  export VENV_MANAGEMENT_SETUP_FILEPATH=$HOME/.venvwraprc

You can also source this custom config file in a shell-specific ``rc`` file using the ``source`` or ``.`` command,
so that ``virtualenvwrapper`` could be used in interactive shells.

.. inclusion-end-configuration-marker-do-not-remove


Release process
===============


Upgrade the version::

    $ bumpversion <major | minor | patch>

Push the tagged commit into the repository together with the tag. You can find the latest tag using the
``git tag`` command or find and fill in the most recent tag with ``git describe``::

    $ git push --atomic origin master $(git describe --abbrev=0 --tags)

Create the source and the binary distribution (outputs in the ``dist`` directory)::

    $ python setup.py sdist bdist_wheel

Remove old versions in the ``dist`` directory and use the following command to upload its contents to PyPI::

    $ twine upload dist/* --config-file=<path/to/file/with/credentials.pypirc>

