# -*- coding: utf-8 -*-

from codecs import open
from os import path
from pip.req import parse_requirements
from pip.download import PipSession
from setuptools import setup, find_packages
from turret import __version__


with open(path.join(path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

requirements = [str(r.req) for r in
                parse_requirements('requirements.in', session=PipSession())]
dev_requirements = [str(r.req) for r in
                    parse_requirements('requirements_dev.in', session=PipSession())
                    if r not in requirements]

setup(
    name='turret',
    version=__version__,
    description='Process orchestration tool for software development',
    long_description=long_description,
    url='https://github.com/yatsu/turret',
    author='Masaki Yatsu',
    author_email='yatsu@yatsu.info',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
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
        'dev': dev_requirements
    },
    test_require=['pytest', 'pytest-cov'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'turret=turret.command:main'
        ]
    }
)
