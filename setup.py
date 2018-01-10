#!/usr/bin/env python

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='asyncitertools',
    version='0.0.1',
    author='Simon Gomizelj',
    author_email='simon@vodik.xyz',
    maintainer='Simon Gomizelj',
    maintainer_email='simon@vodik.xyz',
    packages=find_packages(exclude=('tests', 'examples')),
    license='MIT',
    url='http://github.com/vodik/aiorx',
    description='async generator utilities and reactive tools for Python 3.6+',
    long_description=read('README.rst'),
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
