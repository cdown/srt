#!/usr/bin/env python

'''A tiny library for parsing, modifying, and composing SRT files.'''

import functools
import re
from datetime import timedelta
from itertools import groupby


SRT_REGEX = re.compile(
    r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)([^\n]*)\n(.+?)\n\n',
    re.MULTILINE | re.DOTALL,
)


@functools.total_ordering  # pylint: disable=too-few-public-methods
class Subtitle(object):
    r'''
    The metadata relating to a single subtitle. Subtitles are sorted by start
    time by default.

    :param index: The SRT index for this subtitle
    :type index: int
    :param start: The time that the subtitle should start being shown
    :type start: :py:class:`datetime.timedelta`
    :param end: The time that the subtitle should stop being shown
    :type end: :py:class:`datetime.timedelta`
    :param proprietary: Proprietary metadata for this subtitle
    :type proprietary: str
    :param content: The subtitle content
    :type content: str
    '''

    # pylint: disable=too-many-arguments
    def __init__(self, index, start, end, content, proprietary=''):
        self.index = index
        self.start = start
        self.end = end
        self.content = content
        self.proprietary = proprietary

    def __hash__(self):
        return hash(frozenset(self.__dict__.items()))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return self.start < other.start

    def __repr__(self):
        return '<%s:%d>' % (self.__class__.__name__, self.index)

    def to_srt(self):
        r'''
        Convert the current :py:class:`Subtitle` to an SRT block.

        >>> from srt import Subtitle, srt_timestamp_to_timedelta
        >>> sub = Subtitle(
        ...     index=1, start=srt_timestamp_to_timedelta('00:01:02,003'),
        ...     end=srt_timestamp_to_timedelta('00:02:03,004'), content='foo',
        ... )
        >>> sub.to_srt()
        '1\n00:01:02,003 --> 00:02:03,004\nfoo\n\n'

        :returns: The metadata of the current :py:class:`Subtitle` object as an
                  SRT formatted subtitle block
        :rtype: str
        '''
        return '%d\n%s --> %s%s\n%s\n\n' % (
            self.index, timedelta_to_srt_timestamp(self.start),
            timedelta_to_srt_timestamp(self.end), self.proprietary,
            self.content,
        )


def timedelta_to_srt_timestamp(timedelta_timestamp):
    r'''
    Convert a :py:class:`~datetime.timedelta` to an SRT timestamp.

    >>> import srt
    >>> import datetime
    >>> delta = datetime.timedelta(hours=1, minutes=23, seconds=4)
    >>> srt.timedelta_to_srt_timestamp(delta)
    '01:23:04,000'

    :param timedelta_timestamp: The timestamp to convert
    :type timedelta_timestamp: :py:class:`datetime.timedelta`
    :returns: An SRT formatted (HH:MM:SS,mmm) representation of the timestamp
    :rtype: str
    '''
    seconds_in_hour = 3600
    seconds_in_minute = 60

    hrs, secs_remainder = divmod(timedelta_timestamp.seconds, seconds_in_hour)
    mins, secs = divmod(secs_remainder, seconds_in_minute)
    msecs = timedelta_timestamp.microseconds // 1000
    return '%02d:%02d:%02d,%03d' % (hrs, mins, secs, msecs)


def srt_timestamp_to_timedelta(srt_timestamp):
    r'''
    Convert an SRT timestamp to a :py:class:`~datetime.timedelta`.

    >>> import srt
    >>> srt_timestamp = '01:23:04,000'
    >>> srt.srt_timestamp_to_timedelta(srt_timestamp)
    datetime.timedelta(0, 4984)

    :param srt_timestamp: A timestamp in SRT format (HH:MM:SS,mmm)
    :type srt_timestamp: str
    :returns: A timedelta object representing the same timestamp passed in
    :rtype: :py:class:`datetime.timedelta`
    '''
    hrs, mins, secs, msecs = (int(x) for x in re.split('[,:]', srt_timestamp))
    return timedelta(hours=hrs, minutes=mins, seconds=secs, milliseconds=msecs)


def sort_and_reindex(subtitles, start_index=1):
    '''
    Reorder subtitles to be sorted by start time order, and rewrite the indexes
    to be in that same order. This ensures that the SRT file will play in an
    expected fashion after, for example, times were changed in some subtitles
    and they may need to be resorted.

    :param subtitles: :py:class:`Subtitle` objects in any order
    :type subtitles: :term:`iterator` of :py:class:`Subtitle` objects
    :param start_index: the lowest index to use
    :type start_index: int
    '''
    skipped_subs = 0
    for new_index, subtitle in enumerate(sorted(subtitles), start=start_index):
        if not subtitle.content.strip():
            # Drop contentless subtitles, as they don't serve any purpose and
            # might confuse the media player's parser
            skipped_subs += 1
            continue

        subtitle.index = new_index - skipped_subs
        yield subtitle


def parse(srt):
    r'''
    Convert an SRT formatted string to a :term:`generator` of Subtitle objects.

    If you are reading from a file, consider using :py:func:`parse_file`
    instead.

    >>> import srt
    >>> subs = srt.parse("""\
    ... 422
    ... 00:31:39,931 --> 00:31:41,931
    ... Using mainly spoons,
    ...
    ... 423
    ... 00:31:41,933 --> 00:31:43,435
    ... we dig a tunnel under the city and release it into the wild.
    ...
    ... """)
    >>> list(subs)
    [<Subtitle:422>, <Subtitle:423>]

    :param srt: Subtitles in SRT format
    :type srt: str
    :returns: The subtitles contained in the SRT file as py:class:`Subtitle`
              objects
    :rtype: :term:`generator` of :py:class:`Subtitle` objects
    '''
    for match in SRT_REGEX.finditer(srt):
        raw_index, raw_start, raw_end, proprietary, content = match.groups()
        yield Subtitle(
            index=int(raw_index), start=srt_timestamp_to_timedelta(raw_start),
            end=srt_timestamp_to_timedelta(raw_end), content=content,
            proprietary=proprietary,
        )


def parse_file(srt):
    r'''
    Parse an SRT formatted stream into py:func:`Subtitle` objects.

    >>> import srt
    >>> with open('tests/srt_samples/monsters.srt') as srt_f:
    ...     subs = list(srt.parse_file(srt_f))
    ...
    >>> subs
    [<Subtitle:421>, <Subtitle:422>, <Subtitle:423>]

    :param srt: A stream containing SRT formatted data
    :type srt: :py:class:`io.TextIOWrapper`, or something that quacks like one
    :returns: The subtitles contained in the SRT file as Subtitle objects
    :rtype: :term:`generator` of :py:class:`Subtitle` objects
    '''
    srt_chomped = (line.rstrip('\r\n') for line in srt)
    srt_blocks = (
        '\n'.join(srt_lines) + '\n\n'
        for line_has_content, srt_lines in groupby(srt_chomped, bool)
        if line_has_content
    )

    for srt_block in srt_blocks:
        subtitle, = parse(srt_block)
        yield subtitle


def compose(subtitles, reindex=True, start_index=1):
    r'''
    Convert an iterator of :py:class:`Subtitle` objects to a string of joined
    SRT blocks.

    This may be a convienient interface when converting back and forth between
    Python objects and SRT formatted blocks, but you may wish to consider using
    the provided stream interface, :py:func:`compose_file`, instead, which is
    considerably more memory efficient when dealing with particularly large SRT
    data.

    >>> from srt import Subtitle, srt_timestamp_to_timedelta, compose
    >>> subs = [
    ...     Subtitle(
    ...         index=1, start=srt_timestamp_to_timedelta('00:01:02,003'),
    ...         end=srt_timestamp_to_timedelta('00:02:03,004'), content='foo',
    ...     ),
    ...     Subtitle(
    ...         index=2, start=srt_timestamp_to_timedelta('00:03:04,005'),
    ...         end=srt_timestamp_to_timedelta('00:06:07,008'), content='bar',
    ...     ),
    ... ]
    >>> compose(subs)  # doctest: +ELLIPSIS
    '1\n00:01:02,003 --> 00:02:03,004\nfoo\n\n2\n...'

    :param subtitles: The subtitles to convert to SRT blocks
    :type subtitles: :term:`iterator` of :py:class:`Subtitle` objects
    :param reindex: Whether to reindex subtitles based on start time
    :type reindex: bool
    :param start_index: If reindexing, the index to start reindexing from
    :type start_index: int
    :returns: A single SRT formatted string, with each input
              :py:class:`Subtitle` represented as an SRT block
    :rtype: str
    '''
    if reindex:
        subtitles = sort_and_reindex(subtitles, start_index=start_index)
    return ''.join(subtitle.to_srt() for subtitle in subtitles)


def compose_file(subtitles, output, reindex=True, start_index=1):
    r'''
    Stream a sequence of py:class:`Subtitle` objects into an SRT formatted
    stream.

    >>> import tempfile
    >>> from srt import Subtitle, srt_timestamp_to_timedelta, compose_file
    >>> subs = [
    ...     Subtitle(
    ...         index=1, start=srt_timestamp_to_timedelta('00:01:02,003'),
    ...         end=srt_timestamp_to_timedelta('00:02:03,004'), content='foo',
    ...     ),
    ...     Subtitle(
    ...         index=2, start=srt_timestamp_to_timedelta('00:03:04,005'),
    ...         end=srt_timestamp_to_timedelta('00:06:07,008'), content='bar',
    ...     ),
    ... ]
    >>> with tempfile.NamedTemporaryFile(mode='w', encoding='utf8') as srt_f:
    ...    compose_file(subs, srt_f)
    ...
    2

    :param subtitles: :py:class:`Subtitle` objects in the order they should be
                      written to the stream
    :type subtitles: :term:`iterator` of :py:class:`Subtitle` objects
    :param output: A stream to write the resulting SRT blocks to
    :type output: :py:class:`io.TextIOWrapper`, or something that quacks like
                  one
    :param reindex: Whether to reindex subtitles based on start time
    :type reindex: bool
    :param start_index: If reindexing, the index to start reindexing from
    :type start_index: int
    :returns: The number of subtitles that were written to the stream
    :rtype: int
    '''
    num_written = 0

    if reindex:
        subtitles = sort_and_reindex(subtitles, start_index=start_index)

    for num_written, subtitle in enumerate(subtitles, start=1):
        output.write(subtitle.to_srt())

    return num_written
