Configuration
=============

.. include:: ../../README.rst
   :start-after: inclusion-begin-configuration-marker-do-not-remove
   :end-before:  inclusion-end-configuration-marker-do-not-remove


Configuring for use with *pyenv* and *pyenv-virtualenvwrapper*
--------------------------------------------------------------

The `pyenv <https://github.com/pyenv/pyenv>`_ tool helps with managing multiple Python versions
simultaneously. The `pyenv-virtualenvwrapper <https://github.com/pyenv/pyenv-virtualenvwrapper>`_
plugin for *pyenv*, helps with making *virtualenvwrapper* available to Python environments made
using *pyenv*.

Make a file called ``.venvwraprc`` containing command to initialize both *pyenv* and
*pyenv-virtualenvwrapper* according to your needs::

  export PYENV_ROOT=$HOME/.pyenv
  export PATH=$PYENV_ROOT/bin:$PATH
  eval "$(pyenv init -)"
  eval "$(pyenv init --path)"
  pyenv virtualenvwrapper

This file can be placed in, say, your home directory. You can source this file from your preferred
shell's ``rc`` file (*e.g.* ``.bashrc``) in order ensure both *pyenv* and *virtualenvwrapper* are
available in your interactive shell sessions.

In the environment of the Python program which uses this ``venv-management`` package set these
environment variables::

  export VENV_MANAGEMENT_USE_SETUP=yes
  export VENV_MANAGEMENT_SETUP_FILEPATH=$HOME/.venvwraprc

This will allow ``venv-management`` to ensure that *virtualenvwrapper* is properly initialized
before its commands are executed.


Configuring for use with *venv*
-------------------------------

If the *venv* driver is used, the `venv <https://docs.python.org/3/library/venv.html>`_ module is
used to create Python virtual environments. These environments are created in the directory
specified by the ``VENV_MANAGEMENT_VENV_DIR`` environment variable. If this variable is not set,
the default value of ``$WORKON_HOME/<env-name>`` is used. If ``WORKON_HOME`` is not set, the
default value of ``$HOME/.virtualenvs/<env-name>`` is used.
