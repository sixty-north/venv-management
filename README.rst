===============
Venv Management
===============

A Python package for programmatic creation of Python virtual environments

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
