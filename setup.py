# -*- coding: utf-8 -*-

from codecs import open
from os import path
from setuptools import setup, find_packages
from jaffle import __version__


with open(path.join(path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

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
    "pyhcl>=0.3.0",
    "pyzmq",
    "setuptools",
    "tornado>=4.5,<5",
    "traitlets",
    "watchdog>=0.8.0"
]

dev_requirements = [
    "flake8>=3.5.0",
    "pip",
    "pytest>=3.4.0",
    "pytest-tornado>=0.4.0",
    "watchdog>=0.8.0"
]

setup(
    name='jaffle',
    version=__version__,
    description='Python app and process orchestration tool for development environment',
    long_description=long_description,
    url='https://github.com/yatsu/jaffle',
    author='Jaffle Development Team',
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
    test_require=['pytest', 'pytest-tornado'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'jaffle = jaffle.command:main'
        ]
    }
)
