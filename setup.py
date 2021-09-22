from pathlib import Path
from setuptools import setup, find_packages


setup(
    name='venv-management',
    version='1.0.3',
    packages=find_packages('source'),

    author='Sixty North AS',
    author_email='ekaterina@sixty-north.com',
    description='A Python package for programmatic creation of Python virtual environments',
    license='MIT',
    keywords='',
    url='https://github.com/sixty-north/venv-management',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ],
    platforms='any',
    include_package_data=True,
    package_dir={'': 'source'},
    # package_data={'venv_management': . . .},
    install_requires=[],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax, for
    # example: $ pip install -e ".[dev,test]"
    extras_require={
        'dev': ['black', 'bump2version', 'twine'],
        # 'doc': ['sphinx', 'cartouche'],
        'test': ['hypothesis', 'pytest'],
    },
    entry_points={
        # 'console_scripts': [
        #    'venv_management = venv_management.cli:main',
        # ],
    },
    long_description=Path('README.rst').read_text(encoding='utf-8'),
)
