===============
Venv Management
===============

A Python package for programmatic creation of Python virtual environments


Prerequisites
=============

A virtualenvwrapper installation must have been installed and be available in a login shell. The
following virtualenvwrapper implementations have been tested:

  * `virtualenvwrapper <https://pypi.org/project/virtualenvwrapper/>`_
  * `virtualenv-sh <https://pypi.org/project/virtualenv-sh/>`_

Possibly in future we will also support:

  * `pyenv-virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_
  * `pew <https://pypi.org/project/pew/>`_


Shell selection
---------------

This ``venv-management`` package delegates most operations to one of the ``virtualenvwrapper`` tools
listed above which are implemented using shell scripts and shell functions. In order to invoke these
scripts and functions successfully the shell environment mush have been correctly configured. By
default ``venv-management`` attempts to use the current user's preferred shell by examining the
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
the selected shell can only be usefully sources in an interactive shell, set
``VENV_MANAGEMENT_INTERACTIVE_SHELL`` to ``yes``::


  export VENV_MANAGEMENT_INTERACTIVE_SHELL=yes

Should you wish to specify a different file for shell configuration, provide its path in the
``VENV_MANAGEMENT_SETUP_FILEPATH`` environment variable. For example, since ``.bashrc`` returns
immediately in non-interactive shells, and only login shells source ``.profile`` on start-up,
you may want to set up both ``pyenv`` and ``virtualenvwrapper`` in a separate file, in this example
called ``.venvwraprc``::

  export PYENV_ROOT=$HOME/.pyenv
  export PATH=$PYENV_ROOT/bin:$PATH
  eval "$(pyenv init -)"
  eval "$(pyenv init --path)"
  pyenv virtualenvwrapper


If the ``VENV_MANAGEMENT_USE_SETUP`` is set to ``yes``, the script whose filepath is specified in the
``VENV_MANAGEMENT_SETUP_FILEPATH`` variable will be sourced before every command provided by this package::

  export VENV_MANAGEMENT_USE_SETUP=yes
  export VENV_MANAGEMENT_SETUP_FILEPATH=$HOME/.venvwraprc


You can also source this custom config file in a shell-specific ``rc`` file using the ``source`` or ``.`` command,
so that ``virtualenvwrapper`` could be used in interactive shells.


Manual release
==============

Upgrade the version::

    $ bumpversion <major | minor | patch>

Push the tagged commit into the repository together with the tag. You can find the latest tag using the
``git tag`` command or find and fill in the most recent tag with ``git describe``::

    $ git push --atomic origin master $(git describe --abbrev=0 --tags)

Create the source and the binary distribution (outputs in the ``dist`` directory)::

    $ python setup.py sdist bdist_wheel

Remove old versions in the ``dist`` directory and use the following command to upload its contents to PyPI::

    $ twine upload dist/* --config-file=<path/to/file/with/credentials.pypirc>

