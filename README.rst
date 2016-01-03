srt is a tiny Python library for parsing, modifying, and composing `SRT
files`_. Take a look at the quickstart_ for a basic overview of the library.
`Detailed API documentation`_ is also available.

Want to see some examples of its use? Take a look at the srt-tools_ repo.

Why choose this library?
------------------------

- Extremely lightweight, excluding docstrings/comments/etc around 200 SLOC
- High quality test suite using Hypothesis_
- `100% test coverage`_ (including branches)
- `Well documented API`_, at both a high and low level
- Tolerant of many common errors found in real-world SRT files
- Completely Unicode compliant
- Real world tested — used in production to process thousands of SRT files
  every day


.. _quickstart: http://srt.readthedocs.org/en/latest/quickstart.html
.. _`Detailed API documentation`: http://srt.readthedocs.org/en/latest/api.html
.. _srt-tools: https://github.com/cdown/srt-tools
.. _`SRT files`: https://en.wikipedia.org/wiki/SubRip#SubRip_text_file_format
.. _Hypothesis: https://github.com/DRMacIver/hypothesis
.. _`100% test coverage`: https://coveralls.io/github/cdown/srt?branch=develop
.. _`Well documented API`: http://srt.readthedocs.org/en/latest/index.html

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

   pip install tox
   tox -e quick

.. _Tox: https://tox.readthedocs.org
