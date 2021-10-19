===============
Venv Management
===============

A Python package for programmatic creation of Python virtual environments


Prerequisites
=============

A virtualenvwrapper installation must have been installed and be available in a login shell. The
following virtualenvwrapper implementations have been tested:

  * `virtualenvwrapper <https://pypi.org/project/virtualenvwrapper/>`_
  * `virtualenvwrapper-sh <https://pypi.org/project/virtualenv-sh/>`_
  * `pyenv-virtualenvwrapper <https://github.com/pyenv/pyenv-virtualenvwrapper>`_

Possibly in future we will also support:

  * `pyenv-virtualenv <https://github.com/pyenv/pyenv-virtualenv>`_
  * `pew <https://pypi.org/project/pew/>`_


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
