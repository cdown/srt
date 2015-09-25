#!/usr/bin/env python

'''A tiny library for parsing, modifying, and composing SRT files.'''

from __future__ import unicode_literals
import functools
import re
import os
from datetime import timedelta
from itertools import groupby
import logging

try:
    from io import StringIO
except ImportError:  # Python 2 fallback
    from StringIO import StringIO


log = logging.getLogger(__name__)


class UnexpectedEOFError(Exception): pass


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

    def to_srt(self, strict=True):
        r'''
        Convert the current :py:class:`Subtitle` to an SRT block.

        :param bool strict: If disabled, will allow blank lines in the content
                            of the SRT block, which is a violation of the SRT
                            standard and may case your media player to explode
        :returns: The metadata of the current :py:class:`Subtitle` object as an
                  SRT formatted subtitle block
        :rtype: str
        '''
        proprietary_text = ' %s' % self.proprietary if self.proprietary else ''

        if strict:
            content = os.linesep.join(
                line for line in self.content.splitlines() if line
            )
        else:
            content = self.content

        return '%d\n%s --> %s%s\n%s\n\n' % (
            self.index, timedelta_to_srt_timestamp(self.start),
            timedelta_to_srt_timestamp(self.end), proprietary_text, content,
        )


def timedelta_to_srt_timestamp(timedelta_timestamp):
    r'''
    Convert a :py:class:`~datetime.timedelta` to an SRT timestamp.

    >>> delta = datetime.timedelta(hours=1, minutes=23, seconds=4)
    >>> srt.timedelta_to_srt_timestamp(delta)
    '01:23:04,000'
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

    >>> srt.srt_timestamp_to_timedelta('01:23:04,000')
    datetime.timedelta(0, 4984)
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
    :param int start_index: the index to start from
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
    Convert an SRT formatted string (in Python 2, a :class:`unicode` object) to
    a :term:`generator` of Subtitle objects.

    This function works around bugs present in many SRT files, most notably
    that it is designed to not bork when presented with a blank line as part of
    a subtitle's content.

    If you are reading from a file, consider using :py:func:`parse_file`
    instead.

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

    :param str srt: Subtitles in SRT format
    :returns: The subtitles contained in the SRT file as py:class:`Subtitle`
              objects
    :rtype: :term:`generator` of :py:class:`Subtitle` objects
    '''
    srt_handle = StringIO(srt)

    expected_end_state = 'index'
    state = 'index'
    current = {}
    content = []

    for line in srt_handle:
        log.debug('Parsing line %r', line)
        line = line.strip()

        if state == 'index':
            current['index'] = int(line)
            state = 'timestamp'
            log.debug(
                'Parsed index %d, moving to state %s', current['index'], state,
            )
        elif state == 'timestamp':
            # We don't care about index 2 because it's the arrow.
            timestamp_line_parts = line.split(' ', 3)
            if len(timestamp_line_parts) == 4:  # There is proprietary text
                current['proprietary'] = timestamp_line_parts[3]
            current['start'] = \
                srt_timestamp_to_timedelta(timestamp_line_parts[0])
            current['end'] = \
                srt_timestamp_to_timedelta(timestamp_line_parts[2])
            state = 'text'
            log.debug(
                'Parsed timestamp. Start %s, end %s, moving to state %s',
                current['start'], current['end'], state,
            )
        elif state == 'text':
            if line:
                log.debug('Appending line to subtitle content')
                content.append(line)
            else:
                next_line = _peek_line(srt_handle)
                if next_line and not next_line.isdigit():
                    # This SRT file is messed up and contains a blank line in
                    # the subtitle content, but we can roll with it.
                    log.warning(
                        'Blank line with no following index, '
                        'appending line to subtitle content'
                    )
                    content.append(line)
                else:
                    current['content'] = '\n'.join(content)
                    state = 'index'

                    yield Subtitle(**current)

                    log.debug('Subtitle ended with this line')

                    current = {}
                    content = []

    log.debug('Final state is %s', state)

    if state != expected_end_state:
        raise UnexpectedEOFError(
            'EOF when not in final state: (in %s, not %s)' % (
                state, expected_end_state,
            )
        )


def parse_file(srt):
    r'''
    Parse an SRT formatted stream into py:func:`Subtitle` objects.

    >>> with open('monsters.srt') as srt_f:
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
        log.debug('Parsing SRT block: %r', srt_block)
        subtitle, = parse(srt_block)
        log.debug('Parsed subtitle has index %d', subtitle.index)
        yield subtitle


def compose(subtitles, reindex=True, start_index=1, strict=True):
    r'''
    Convert an iterator of :py:class:`Subtitle` objects to a string of joined
    SRT blocks.

    This may be a convienient interface when converting back and forth between
    Python objects and SRT formatted blocks, but you may wish to consider using
    the provided stream interface, :py:func:`compose_file`, instead, which is
    considerably more memory efficient when dealing with particularly large SRT
    data.

    >>> subs = [Subtitle(...), Subtitle(...)]
    >>> compose(subs)
    '1\n00:01:02,003 --> 00:02:03,004\nfoo\n\n2\n...'

    :param subtitles: The subtitles to convert to SRT blocks
    :type subtitles: :term:`iterator` of :py:class:`Subtitle` objects
    :param bool reindex: Whether to reindex subtitles based on start time
    :param int start_index: If reindexing, the index to start reindexing from
    :type start_index: int
    :param bool strict: Whether to enable strict mode, see
                        :py:func:`Subtitle.to_srt` for more information
    :returns: A single SRT formatted string, with each input
              :py:class:`Subtitle` represented as an SRT block
    :rtype: str
    '''
    if reindex:
        subtitles = sort_and_reindex(subtitles, start_index=start_index)
    return ''.join(subtitle.to_srt(strict=strict) for subtitle in subtitles)


def compose_file(subtitles, output, reindex=True, start_index=1, strict=True):
    r'''
    Stream a sequence of py:class:`Subtitle` objects into an SRT formatted
    stream.

    >>> subs = [Subtitle(...), Subtitle(...)]
    >>> with tempfile.NamedTemporaryFile(mode='w', encoding='utf8') as srt_f:
    ...    compose_file(subs, srt_f)
    2

    :param subtitles: :py:class:`Subtitle` objects in the order they should be
                      written to the stream
    :type subtitles: :term:`iterator` of :py:class:`Subtitle` objects
    :param output: A stream to write the resulting SRT blocks to
    :type output: :py:class:`io.TextIOWrapper`, or something that quacks like
                  one
    :param bool reindex: Whether to reindex subtitles based on start time
    :param int start_index: If reindexing, the index to start reindexing from
    :param bool strict: Whether to enable strict mode, see
                        :py:func:`Subtitle.to_srt` for more information
    :returns: The number of subtitles that were written to the stream
    '''
    num_written = 0

    if reindex:
        subtitles = sort_and_reindex(subtitles, start_index=start_index)

    for num_written, subtitle in enumerate(subtitles, start=1):
        output.write(subtitle.to_srt(strict=strict))

    return num_written


def _peek_line(file_obj):
    pos = file_obj.tell()
    line = file_obj.readline()
    file_obj.seek(pos)
    return line[:-1]  # chomp
