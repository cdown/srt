#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_f:
    README = readme_f.read()

setup(
    name='srt',
    version='1.0.0',
    description='A tiny library for parsing, modifying, and composing SRT '
                'files.',
    long_description=README,
    author='Chris Down',
    author_email='chris@chrisdown.name',
    url='https://github.com/cdown/srt',
    py_modules=['srt'],
    license='Public Domain',
    keywords='srt',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Video',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing',
    ],
)
