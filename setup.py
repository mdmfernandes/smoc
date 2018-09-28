#!/usr/bin/env python
# This file is part of SMOC
# Copyright (C) 2018  Miguel Fernandes
#
# SMOC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SMOC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='SMOC',
    version='0.1.0',
    description='A Stochastic Multi-objective Optimizer for Cadence Virtuoso',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Miguel Fernandes',
    author_email='projects@mdmfernandes.com',
    url='https://github.com/mdmfernandes/smoc',
    packages=find_packages(),
    keywords=[
        'evolutionary algorithms', 'genetic algorithms', 'nsga-ii', 'circuit optimization',
        'electronic design automation', 'cadence virtuoso'
    ],
    platforms=['any'],
    license='GPLv3',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'Topic :: Software Development :: Genetic Algorithm'
    ],
    entry_points={
        'console_scripts': [
            'smoc = smoc.__main__:main'
        ]
    },
    python_requires='>=3.6',
    install_requires=[
        'deap>=1.2.2',
        'bokeh>=0.13.0',
        'tqdm>=4.25.0',
        'pyyaml>=3.13'
    ]
)
