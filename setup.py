#!/usr/bin/env python


from setuptools import setup, find_packages
from codecs import open 
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description  = f.read()

import pycdl

requires = []

setup(
    name='pycdl',
    version=pycdl.__version__,
    description='Simple CDL reading library',
    long_description=long_description,
    author='Simon Hargreaves',
    author_email='simon@simon-hargreaves.com',
    license='MIT',
    url='https://github.com/simonh10/pycdl',
    packages=['pycdl'],
    classifiers=[
       'Development Status :: 4 - Beta',
       'Environment :: Console',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: MIT License',
       'Operating System :: MacOS :: MacOS X',
       'Operating System :: Microsoft :: Windows',
       'Operating System :: POSIX',
       'Programming Language :: Python',
       'Natural Language :: English',
       'Topic :: Multimedia :: Video',
       'Topic :: Software Development :: Libraries'
    ],
    keywords='color cdl edl decision list avid'
)