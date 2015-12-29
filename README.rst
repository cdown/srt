srt is a tiny Python library for parsing, modifying, and composing `SRT
files`_. Take a look at the quickstart_ for a basic overview of the library.
`Detailed API documentation`_ is also available.

Why choose this library? Well, it's:

- Very fast (shifting the time on 50 2-hour SRT subtitles takes around 2
  seconds on a fairly recent machine);
- All functionality is covered with tests;
- Able to parse many not-totally-legal SRT files without sacrificing
  performance (for example, SRT files with blank lines in the content, and
  proprietary metadata after the timestamps);
- Completely Unicode compliant both on Python 2 and 3;
- Small (excluding docstrings/blank lines/etc, only a little more than 100
  lines of code);
- Complete -- currently used in production every day on real-world SRT files.

Want to see some real-world examples of its use? Take a look at the srt-tools_
repo.

.. _quickstart: http://srt.readthedocs.org/en/latest/quickstart.html
.. _`Detailed API documentation`: http://srt.readthedocs.org/en/latest/api.html
.. _srt-tools: https://github.com/cdown/srt-tools
.. _`SRT files`: https://en.wikipedia.org/wiki/SubRip#SubRip_text_file_format

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

|travis| |coveralls|

.. |travis| image:: https://travis-ci.org/cdown/srt.svg?branch=develop
  :target: https://travis-ci.org/cdown/srt
  :alt: Test status

.. |coveralls| image:: https://coveralls.io/repos/cdown/srt/badge.svg?branch=develop&service=github
  :target: https://coveralls.io/github/cdown/srt?branch=develop
  :alt: Coverage

.. code::

   tox -e quick

.. _Tox: https://tox.readthedocs.org
