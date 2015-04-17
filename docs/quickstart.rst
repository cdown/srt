Quickstart
==========

Parse an SRT to Python objects
------------------------------

.. doctest::

    >>> import srt
    >>> subtitle_generator = srt.parse('''\
    ... 1
    ... 00:31:37,894 --> 00:31:39,928
    ... OK, look, I think I have a plan here.
    ...
    ... 2
    ... 00:31:39,931 --> 00:31:41,931
    ... Using mainly spoons,
    ...
    ... 3
    ... 00:31:41,933 --> 00:31:43,435
    ... we dig a tunnel under the city and release it into the wild.
    ...
    ... ''')
    >>> subtitles = list(subtitle_generator)
    >>>
    >>> subtitles[0].start
    datetime.timedelta(0, 1897, 894000)
    >>> subtitles[1].content
    'Using mainly spoons,'

You can also read from a file:

.. code:: python

    >>> with open('mwazowski.srt') as srt_f:
    ...     subtitle_generator = srt.parse_file(srt_f)

Compose an SRT from Python objects
----------------------------------

.. doctest::

    >>> print(srt.compose(subtitles))
    1
    00:31:37,894 --> 00:31:39,928
    OK, look, I think I have a plan here.
    <BLANKLINE>
    2
    00:31:39,931 --> 00:31:41,931
    Using mainly spoons,
    <BLANKLINE>
    3
    00:31:41,933 --> 00:31:43,435
    we dig a tunnel under the city and release it into the wild.
    <BLANKLINE>
    <BLANKLINE>

You can also write to a file:

.. code:: python

    >>> with open('mwazowski.srt', 'w') as srt_f:
    ...     srt.compose_file(subtitles, srt_f)
