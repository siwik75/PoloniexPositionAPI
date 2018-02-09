#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: Put package requirements here
]

setup_requirements = [
    # TODO(siwik75): Put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: Put package test requirements here
]

setup(
    name='poloniexpositionapi',
    version='0.1.0',
    description="Using Poloniex API - gathers your Balance and All trades to determine your gain/loss on current position and per coin basis.",
    long_description=readme + '\n\n' + history,
    author="Simone Paganini",
    author_email='simon.siwik@gmail.com',
    url='https://github.com/siwik75/poloniexpositionapi',
    packages=find_packages(include=['poloniexpositionapi']),
    entry_points={
        'console_scripts': [
            'poloniexpositionapi=poloniexpositionapi.cli:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='poloniexpositionapi',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
