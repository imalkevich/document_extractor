#!/usr/bin/env python

from setuptools import setup, find_packages
import errorguimonitor
import os


def extra_dependencies():
    import sys
    ret = []
    if sys.version_info < (2, 7):
        ret.append('argparse')
    return ret


def read(*names):
    values = dict()
    extensions = ['.txt', '.rst']
    for name in names:
        value = ''
        for extension in extensions:
            filename = name + extension
            if os.path.isfile(filename):
                value = open(name + extension).read()
                break
        values[name] = value
    return values

long_description = """
%(README)s

News
====

%(CHANGES)s

""" % read('README', 'CHANGES')

setup(
    name='document_extractor',
    version=errorguimonitor.__version__,
    description='Extract specific portions of document text from XML',
    long_description=long_description,
    classifiers=[
        "Development Status :: 1 - Development",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Documentation",
    ],
    keywords='document extract XML',
    author='Ihar Malkevich',
    author_email='imalkevich@gmail.com',
    maintainer='Ihar Malkevich',
    maintainer_email='imalkevich@gmail.com',
    url='https://github.com/imalkevich/document_extractor',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'document_extractor = document_extractor.extractor:command_line_runner',
        ]
    },
    install_requires=[
        'requests'
    ] + extra_dependencies(),
    test_require = ['coverage', 'codecov']
)
