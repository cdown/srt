|travis| |appveyor| |coveralls| |libraries|

.. |travis| image:: https://img.shields.io/travis/cdown/srt/develop.svg?label=linux%20%2B%20mac%20tests
  :target: https://travis-ci.org/cdown/srt
  :alt: Linux and Mac tests

.. |appveyor| image:: https://img.shields.io/appveyor/ci/cdown/srt/develop.svg?label=windows%20tests
  :target: https://ci.appveyor.com/project/cdown/srt
  :alt: Windows tests

.. |coveralls| image:: https://img.shields.io/coveralls/cdown/srt/develop.svg?label=test%20coverage
  :target: https://coveralls.io/github/cdown/srt?branch=develop
  :alt: Coverage

.. |libraries| image:: https://img.shields.io/librariesio/github/cdown/srt.svg?label=dependencies
  :target: https://libraries.io/github/cdown/srt
  :alt: Dependencies

srt is a tiny but featureful Python library for parsing, modifying, and
composing `SRT files`_. Take a look at the quickstart_ for a basic overview of
the library. `Detailed API documentation`_ is also available.

Want to see some examples of its use? Take a look at the `tools shipped with
the library`_.

Why choose this library?
------------------------

- Extremely lightweight, `~150 lines of code`_ excluding docstrings
- Simple, intuitive API
- High quality test suite using Hypothesis_
- `100% test coverage`_ (including branches)
- `Well documented API`_, at both a high and low level
- `~30% faster than pysrt on typical workloads`_
- Native support for Python 2 and 3
- Full support for `PyPy`_
- No dependencies outside of the standard library
- Tolerant of many common errors found in real-world SRT files
- Support for Asian-style SRT formats (ie. "fullwidth" SRT format)
- Completely Unicode compliant
- `Released into the public domain`_
- Real world tested — used in production to process thousands of SRT files
  every day
- Portable — runs on Linux, OSX, and Windows
- Tools included — contains lightweight tools to perform generic tasks with the
  library

.. _quickstart: http://srt.readthedocs.org/en/latest/quickstart.html
.. _`SRT files`: https://en.wikipedia.org/wiki/SubRip#SubRip_text_file_format
.. _Hypothesis: https://github.com/DRMacIver/hypothesis
.. _`100% test coverage`: https://coveralls.io/github/cdown/srt?branch=develop
.. _`Well documented API`: http://srt.readthedocs.org/en/latest/index.html
.. _`Released into the public domain`: https://cr.yp.to/publicdomain.html
.. _`~150 lines of code`: https://paste.pound-python.org/raw/3WgFQIvkVVvBZvQI3nm4/
.. _PyPy: http://pypy.org/
.. _`~30% faster than pysrt on typical workloads`: https://paste.pound-python.org/raw/8nQKbDW0ROWvS7bOeAb3/

Usage
-----

Tools
=====

There are a number of `tools shipped with the library`_ to manipulate, process,
and fix SRT files. Here's an example using `hanzidentifier`_ to strip out
non-Chinese lines:

.. code::

    $ cat pe.srt
    1
    00:00:33,843 --> 00:00:38,097
    Only 3% of the water on our planet is fresh.
    地球上只有3%的水是淡水

    2
    00:00:40,641 --> 00:00:44,687
    Yet, these precious waters are rich with surprise.
    可是这些珍贵的淡水中却充满了惊奇

    $ srt lines-matching -m hanzidentifier -f hanzidentifier.has_chinese -i pe.srt
    1
    00:00:33,843 --> 00:00:38,097
    地球上只有3%的水是淡水

    2
    00:00:40,641 --> 00:00:44,687
    可是这些珍贵的淡水中却充满了惊奇


These tools are easy to chain together, for example, say you have one subtitle
with Chinese and English, and other with French, but you want Chinese and
French only. Oh, and the Chinese one is 5 seconds later than it should be.
That's easy enough to sort out:

.. code::

   $ srt lines-matching -m hanzidentifier -f hanzidentifier.has_chinese -i chs+eng.srt |
   >     srt fixed-timeshift --seconds -5 |
   >     srt mux --input - --input fra.srt

See the srt_tools/ directory for more information.

.. _hanzidentifier: https://github.com/tsroten/hanzidentifier

Library
=======

`Detailed API documentation`_ is available, but here are the basics:

.. code:: python

    >>> # list() is needed as srt.parse creates a generator
    >>> subs = list(srt.parse('''\
    ... 1
    ... 00:00:33,843 --> 00:00:38,097
    ... 地球上只有3%的水是淡水
    ...
    ... 2
    ... 00:00:40,641 --> 00:00:44,687
    ... 可是这些珍贵的淡水中却充满了惊奇
    ...
    ... 3
    ... 00:00:57,908 --> 00:01:03,414
    ... 所有陆地生命归根结底都依赖於淡水
    ...
    ... '''))
    >>> subs
    [Subtitle(index=1, start=datetime.timedelta(0, 33, 843000), end=datetime.timedelta(0, 38, 97000), content='地球上只有3%的水是淡水', proprietary=''),
     Subtitle(index=2, start=datetime.timedelta(0, 40, 641000), end=datetime.timedelta(0, 44, 687000), content='可是这些珍贵的淡水中却充满了惊奇', proprietary=''),
     Subtitle(index=3, start=datetime.timedelta(0, 57, 908000), end=datetime.timedelta(0, 63, 414000), content='所有陆地生命归根结底都依赖於淡水', proprietary='')]
    >>> print(srt.compose(subs))
    1
    00:00:33,843 --> 00:00:38,097
    地球上只有3%的水是淡水

    2
    00:00:40,641 --> 00:00:44,687
    可是这些珍贵的淡水中却充满了惊奇

    3
    00:00:57,908 --> 00:01:03,414
    所有陆地生命归根结底都依赖於淡水

Installation
------------

To install the latest stable version from PyPi:

.. code::

    pip install -U srt

To install the latest development version directly from GitHub:

.. code::

    pip install -U git+https://github.com/cdown/srt.git@develop

Testing
-------

.. code::

   tox

.. _Tox: https://tox.readthedocs.org
.. _`Detailed API documentation`: http://srt.readthedocs.org/en/latest/api.html
.. _`tools shipped with the library`: https://github.com/cdown/srt/tree/develop/srt_tools
