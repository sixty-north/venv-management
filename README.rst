===============
Venv Management
===============

A Python package for programmatic creation and management of Python virtual environments.


.. image:: https://github.com/sixty-north/venv-management/actions/workflows/actions.yml/badge.svg
     :target: https://github.com/sixty-north/venv-management/actions?workflow=CI
     :alt: CI Status

.. image:: https://readthedocs.org/projects/venv-management/badge/?version=latest
    :target: https://venv-management.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


This document gives an overview. For more detail see the `documentation <https://venv-management.readthedocs.io/en/latest/?badge=latest>`_.


Prerequisites
=============

None, other than a working Python installation, though depending on which virtual environment
management tool you wish to use, there may be additional requirements. The following are supported:

  * `venv <https://docs.python.org/3/library/venv.html>`_
  * `virtualenvwrapper <https://pypi.org/project/virtualenvwrapper/>`_
  * `virtualenv-sh <https://pypi.org/project/virtualenv-sh/>`_
  * `pyenv-virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_

Possibly in future we will also support:

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
equivalent tools, some of which are implemented using shell scripts and shell functions.
In order to invoke these scripts and functions successfully the shell environment mush have been
correctly configured. By default ``venv-management`` attempts to use the current user's preferred
shell by examining the ``$SHELL`` environment variable. This can be overridden by setting the
``$VENV_MANAGEMENT_SHELL`` variable with a shell executable name or the path to a shell executable,
for example::

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

You can also source this custom config file in a shell-specific ``rc`` file using the ``source`` or
``.`` command,
so that ``virtualenvwrapper`` could be used in interactive shells.

Driver preference
-----------------

If you have multiple virtualenv wrapper implementations installed, you can specify the order in
which they will be tried with the ``VENV_MANAGEMENT_PREFERRED_DRIVERS`` environment variable. The
first working implementation will be used::

  export VENV_MANAGEMENT_PREFERRED_DRIVERS="virtualenvwrapper,virtualenv-sh,venv"

You can also exclude a driver from consideration by using the ``VENV_MANAGEMENT_EXCLUDED_DRIVERS``::

  export VENV_MANAGEMENT_EXCLUDED_DRIVERS="venv"

.. inclusion-end-configuration-marker-do-not-remove
