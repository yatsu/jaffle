# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from turret import __version__


setup(
    name='turret_tornado_spa_example',
    version=__version__,
    description='Turret tornado SPA example',
    long_description='',
    author='Turret Development Team',
    packages=find_packages(),
    install_requires=['tornado'],
    test_require=['pytest', 'pytest-tornado'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'turret-tornado-spa-example = turret_tornado_spa_example.app:main'
        ]
    }
)
