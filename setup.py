#!/usr/bin/env python

import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with codecs.open("README.rst", encoding="utf8") as readme_f:
    README = readme_f.read()

setup(
    name="srt",
    version="1.11.0",
    description="A tiny library for parsing, modifying, and composing SRT " "files.",
    long_description=README,
    author="Chris Down",
    author_email="chris@chrisdown.name",
    url="https://github.com/cdown/srt",
    py_modules=["srt", "srt_tools.utils"],
    scripts=[
        "srt_tools/srt",
        "srt_tools/srt-fix-subtitle-indexing",
        "srt_tools/srt-fixed-timeshift",
        "srt_tools/srt-linear-timeshift",
        "srt_tools/srt-lines-matching",
        "srt_tools/srt-mux",
        "srt_tools/srt-play",
        "srt_tools/srt-process",
    ],
    license="Public Domain",
    keywords="srt",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing",
    ],
)
