# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from jaffle import __version__


setup(
    name='jupyter_myext',
    version=__version__,
    description='Jupyter extension example',
    long_description='',
    author='Jaffle Development Team',
    packages=find_packages(),
    install_requires=['notebook'],
    test_require=['pytest', 'pytest-tornado'],
    include_package_data=True
)
