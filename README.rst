srt is a tiny Python library for parsing, modifying, and composing `SRT
files`_. Take a look at the quickstart_ for a basic overview of the library.
`Detailed API documentation`_ is also available.

Want to see some real-world examples? Take a look at the srt-tools_ repo.

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

|travis| |coveralls| |scrutinizer|

.. |travis| image:: https://travis-ci.org/cdown/srt.svg?branch=develop
  :target: https://travis-ci.org/cdown/srt
  :alt: Test status

.. |coveralls| image:: https://coveralls.io/repos/cdown/srt/badge.svg?branch=develop&service=github
  :target: https://coveralls.io/github/cdown/srt?branch=develop
  :alt: Coverage

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/cdown/srt/develop.svg
  :target: https://scrutinizer-ci.com/g/cdown/srt/?branch=develop
  :alt: Code quality

.. code::

   tox -e quick

.. _Tox: https://tox.readthedocs.org
