Quickstart
==========

Parse an SRT to Python objects
------------------------------

.. code:: python

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

Compose an SRT from Python objects
----------------------------------

.. code:: python

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

Newlines
--------

srt accepts ``\r\n`` line endings, but converts them to ``\n`` internally. One
reason for this is because it's impossible for srt to know whether you're using
universal newlines, and even if you're not, whether you're going to write in
text mode or binary mode.

As such, if you want output with a line ending *other* than ``\n``, it's your
responsibility to do something like this (the default ``eol`` is ``\n`` for
these reasons).

.. code:: python

    srt.compose(subs, eol=os.linesep)
