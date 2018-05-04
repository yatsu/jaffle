# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from jaffle import __version__


setup(
    name='tornado_spa',
    version=__version__,
    description='Jaffle tornado SPA example',
    long_description='',
    author='Jaffle Development Team',
    packages=find_packages(),
    install_requires=['tornado'],
    test_require=['pytest', 'pytest-tornado'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'jaffle-tornado-spa-example = tornado_spa.app:main'
        ]
    }
)
