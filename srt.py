#!/usr/bin/env python

'''A tiny library for parsing, modifying, and composing SRT files.'''

from __future__ import unicode_literals
import functools
import re
from datetime import timedelta
import logging


log = logging.getLogger(__name__)

SRT_REGEX = re.compile(
    r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+) ?([^\n]*)\n(.*?)'
    # Many sub editors don't add a blank line to the end, and many editors
    # accept it. We allow it in input.
    r'(?:\n|\Z)(?:\n|\Z)'
    # Some SRT blocks, while this is technically invalid, have blank lines
    # inside the subtitle content. We look ahead a little to check that the
    # next lines look like an index and a timestamp as a best-effort
    # solution to work around these.
    r'(?=(?:\d+\n\d+:|\Z))',
    re.MULTILINE | re.DOTALL,
)

SECONDS_IN_HOUR = 3600
SECONDS_IN_MINUTE = 60
HOURS_IN_DAY = 24


@functools.total_ordering
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

    def __init__(self, index, start, end, content, proprietary=''):
        self.index = index
        self.start = start
        self.end = end
        self.content = content
        self.proprietary = proprietary

    def __hash__(self):
        return hash(frozenset(vars(self).items()))

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __lt__(self, other):
        return self.start < other.start

    def __repr__(self):
        return '<%s, index %d, from %s to %s (%r)>' % (
            type(self).__name__, self.index,
            timedelta_to_srt_timestamp(self.start),
            timedelta_to_srt_timestamp(self.end),
            self.content[:20],
        )

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
        output_content = self.content
        output_proprietary = self.proprietary

        if output_proprietary:
            # output_proprietary is output directly next to the timestamp, so
            # we need to add the space as a field delimiter.
            output_proprietary = ' ' + output_proprietary

        if strict:
            output_content = make_legal_content(output_content)

        return '%d\n%s --> %s%s\n%s\n\n' % (
            self.index, timedelta_to_srt_timestamp(self.start),
            timedelta_to_srt_timestamp(self.end), output_proprietary,
            output_content,
        )


def make_legal_content(content):
    r'''
    Remove illegal content from a content block. Illegal content includes:

    * Blank lines
    * Starting or ending with a blank line

    >>> srt.make_legal_content('\nfoo\n\nbar\n')
    'foo\nbar'

    :param srt content: the content to make legal
    :returns: the legalised content
    :rtype: srt
    '''
    # We can't use content.splitlines() here since it does all sorts of stuff
    # that we don't want with \x1{c..e}, etc
    legal_content = '\n'.join(line for line in content.split('\n') if line)
    if legal_content != content:
        log.warning('Legalised content %r to %r', content, legal_content)
    return legal_content


def timedelta_to_srt_timestamp(timedelta_timestamp):
    r'''
    Convert a :py:class:`~datetime.timedelta` to an SRT timestamp.

    >>> delta = datetime.timedelta(hours=1, minutes=23, seconds=4)
    >>> srt.timedelta_to_srt_timestamp(delta)
    '01:23:04,000'
    '''

    hrs, secs_remainder = divmod(timedelta_timestamp.seconds, SECONDS_IN_HOUR)
    hrs += timedelta_timestamp.days * HOURS_IN_DAY
    mins, secs = divmod(secs_remainder, SECONDS_IN_MINUTE)
    msecs = timedelta_timestamp.microseconds // 1000
    return '%02d:%02d:%02d,%03d' % (hrs, mins, secs, msecs)


def srt_timestamp_to_timedelta(srt_timestamp):
    r'''
    Convert an SRT timestamp to a :py:class:`~datetime.timedelta`.

    >>> srt.srt_timestamp_to_timedelta('01:23:04,000')
    datetime.timedelta(0, 4984)
    '''
    # "." is not technically a legal separator, but some subtitle editors use
    # it to delimit msecs, and some players accept it.
    hrs, mins, secs, msecs = (int(x) for x in re.split('[,:.]', srt_timestamp))
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
            log.warning(
                'Skipped contentless subtitle that was at index %d',
                subtitle.index,
            )
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

    expected_start = 0

    for match in SRT_REGEX.finditer(srt):
        actual_start = match.start()
        _raise_if_not_contiguous(srt, expected_start, actual_start)

        raw_index, raw_start, raw_end, proprietary, content = match.groups()
        yield Subtitle(
            index=int(raw_index), start=srt_timestamp_to_timedelta(raw_start),
            end=srt_timestamp_to_timedelta(raw_end), content=content,
            proprietary=proprietary,
        )

        expected_start = match.end()

    _raise_if_not_contiguous(srt, expected_start, len(srt))


def _raise_if_not_contiguous(srt, expected_start, actual_start):
    '''
    Raise :py:class:`SRTParseError` with diagnostic info if expected_start does
    not equal actual_start.

    :param str srt: the data being matched
    :param int expected_start: the expected next start, as from the last
                               iteration's match.end()
    :param int actual_start: the actual start, as from this iteration's
                             match.start()
    :raises SRTParseError: if the matches are not contiguous
    '''
    if expected_start != actual_start:
        raise SRTParseError(
            'Expected contiguous start of match or end of string at char %d, '
            'but started at char %d (unmatched content: %r)' % (
                expected_start, actual_start, srt[expected_start:actual_start],
            )
        )


def compose(subtitles, reindex=True, start_index=1, strict=True):
    r'''
    Convert an iterator of :py:class:`Subtitle` objects to a string of joined
    SRT blocks.

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


class SRTParseError(Exception):
    '''
    Raised when an error is encountered parsing an SRT block.
    '''
