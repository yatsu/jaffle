# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from turret import __version__


setup(
    name='turret_pytest_example',
    version=__version__,
    description='Turret pytest example',
    long_description='',
    author='Turret Development Team',
    packages=find_packages(),
    install_requires=['turret', 'pytest', 'watchdog'],
    test_require=['pytest'],
    include_package_data=True
)
