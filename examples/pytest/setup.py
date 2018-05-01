# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from jaffle import __version__


setup(
    name='jaffle_pytest_example',
    version=__version__,
    description='Jaffle pytest example',
    long_description='',
    author='Jaffle Development Team',
    packages=find_packages(),
    install_requires=['jaffle', 'pytest', 'watchdog'],
    test_require=['pytest'],
    include_package_data=True
)
