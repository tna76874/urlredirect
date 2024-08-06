#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from setuptools import find_packages, setup

from version import *
package_version = GitVersion('./client')

setup(
    name='urlclient',
    version=package_version._get_semantic_version(),
    description='Url Redirekt Client',
    url='https://github.com/tna76874',
    author='lmh',
    author_email='',
    license='BSD 2-clause',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Requests",
        "tqdm",
        "pandas",
        "openpyxl",
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires = ">=3.6",
    entry_points={
        "console_scripts": [
            "urlmanage = client.cli:main",
        ],
    },
    )
