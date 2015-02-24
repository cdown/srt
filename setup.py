#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_f:
    readme = readme_f.read()

with open('tests/requirements.txt') as test_requirements_f:
    test_requirements = test_requirements_f.readlines()

setup(
    name='tinysrt',
    version='0.0.1',
    description='A tiny library for parsing, modifying, and composing SRT files.',
    long_description=readme,
    author='Chris Down',
    author_email='chris@chrisdown.name',
    url='https://github.com/cdown/tinysrt',
    py_modules=['tinysrt'],
    license='ISC',
    zip_safe=False,
    keywords='tinysrt',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='nose.collector',
    tests_require=test_requirements
)
