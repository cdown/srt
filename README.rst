===
srt
===

srt is a tiny Python library for parsing, modifying, and composing SRT files.

Documentation
-------------

If you're new to the library, take a look at the quickstart_ for ideas about
how to use it. `Detailed API documentation`_ is also available.

Want to see some real-world examples? Take a look at the srt-tools_ repo.

.. _quickstart: http://srt.readthedocs.org/en/latest/quickstart.html
.. _`Detailed API documentation`: http://srt.readthedocs.org/en/latest/api.html
.. _srt-tools: https://github.com/cdown/srt-tools


Installation
------------

From pip:

.. code::

    $ pip install srt

Manually:

.. code::

    $ python setup.py install


Testing
-------

.. image:: https://travis-ci.org/cdown/srt.svg?branch=develop
  :target: https://travis-ci.org/cdown/srt
  :alt: Test status

First, install the test requirements:

.. code::

    $ pip install -r tests/requirements.txt

Then, to test using your current Python interpreter:

.. code::

    $ nosetests

Otherwise, to test on all supported Python versions:

.. code::

    $ tox
