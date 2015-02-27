Quickstart
==========

srt is a tiny Python library for parsing, modifying, and composing SRT files.

Parse an SRT to Python objects
------------------------------

.. code:: python

    >>> subtitle_generator = tinysrt.parse('''\
    ... 421
    ... 00:31:37,894 --> 00:31:39,928
    ... OK, look, I think I have a plan here.
    ...
    ... 422
    ... 00:31:39,931 --> 00:31:41,931
    ... Using mainly spoons,
    ...
    ... 423
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
    ...     subtitle_generator = tinysrt.parse_file(srt_f)

Compose an SRT from Python objects
----------------------------------

.. code:: python

    >>> print(tinysrt.compose(subtitles))
    421
    00:31:37,894 --> 00:31:39,928
    OK, look, I think I have a plan here.

    422
    00:31:39,931 --> 00:31:41,931
    Using mainly spoons,

    423
    00:31:41,933 --> 00:31:43,435
    we dig a tunnel under the city and release it into the wild.

You can also write to a file:

.. code:: python

    >>> with open('mwazowski.srt') as srt_f:
    ...     tinysrt.compose_file(subtitles, srt_f)

