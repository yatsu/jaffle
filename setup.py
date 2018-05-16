# -*- coding: utf-8 -*-
# flake8: noqa

import os
from setuptools import setup, find_packages
from jaffle import __version__


long_description = '''
Jaffle is an automation tool for Python software development, which does:

- Instantiate Python applications in a Jupyter kernel and allows them to call
  each other
- Launch external processes
- Combine log messages of all Python applications and external processes
  enabling filtering and reformatting

Jaffle contains WatchdogApp that can watch filesystem events and call
arbitrary code or command. That allows you to automate testing, reloading
applications, etc.

Examples
========

- `Auto-testing with pytest`_
- `Automatic Sphinx Document Build`_
- `Web Development with Tornado and React`_
- `Jupyter Extension Development`_

.. _`Auto-testing with pytest`: http://jaffle.readthedocs.io/en/latest/cookbook/pytest.html
.. _`Automatic Sphinx Document Build`: http://jaffle.readthedocs.io/en/latest/cookbook/sphinx.html
.. _`Web Development with Tornado and React`: http://jaffle.readthedocs.io/en/latest/cookbook/tornado_spa.html
.. _`Jupyter Extension Development`: http://jaffle.readthedocs.io/en/latest/cookbook/jupyter_ext.html

GitHub Respository
==================

`yatsu/jaffle`_

.. _`yatsu/jaffle`: https://github.com/yatsu/jaffle

Documentation
=============

`Jaffle documentation`_

.. _`Jaffle documentation`: http://jaffle.readthedocs.io
'''.strip()

requirements = [
    "filelock>=3.0.0,<4",
    "ipython",
    "jupyter-client",
    "jupyter-console",
    "jupyter-core",
    "mako>=1.0.0",
    "notebook>=5.0.0,<6",
    "prompt-toolkit",
    "pygments",
    "pyyaml",
    "pyzmq",
    "setuptools",
    "tornado>=4.5,<5",
    "traitlets",
    "watchdog>=0.8.0"
]

if os.getenv('READTHEDOCS') != 'True':
    requirements += [
        "pyhcl>=0.3.0",
        "pyjq>=2.1.0"
    ]

dev_requirements = [
    "flake8>=3.5.0",
    "pip",
    "pytest>=3.4.0",
    "pytest-cov>=2.5.0",
    "pytest-tornado>=0.4.0",
    "watchdog>=0.8.0"
]

setup(
    name='jaffle',
    version=__version__,
    description='Python app and process orchestration tool for development environment',
    long_description=long_description,
    author='Jaffle Development Team',
    author_email='jaffle@yatsu.info',
    url='https://github.com/yatsu/jaffle',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Shells',
        'Topic :: Utilities'
    ],
    keywords='orchestration interactive process test pytest watchdog',
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'pytest': ['pytest>=3.4.0']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'jaffle = jaffle.command:main'
        ]
    }
)
