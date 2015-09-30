#!/usr/bin/env python

'''A tiny library for parsing, modifying, and composing SRT files.'''

from __future__ import unicode_literals
import functools
import re
import os
from datetime import timedelta
import logging


log = logging.getLogger(__name__)

SRT_REGEX = re.compile(
    r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)([^\n]*)\n'
    r'(.+?)\n\n(?=(\d+\n\d+:|\Z))',
    re.MULTILINE | re.DOTALL,
)


class SRTParseError(Exception): pass


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
        if strict:
            content = os.linesep.join(
                line for line in self.content.splitlines() if line
            )
        else:
            content = self.content

        return '%d\n%s --> %s%s\n%s\n\n' % (
            self.index, timedelta_to_srt_timestamp(self.start),
            timedelta_to_srt_timestamp(self.end), self.proprietary, content,
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
    # We use match_ranges to check that the regexes were contiguous and
    # consumed all of the string, without silently ignoring anything.
    match_ranges = []

    for match in SRT_REGEX.finditer(srt):
        match_ranges.append((match.start(), match.end()))
        raw_index, raw_start, raw_end, proprietary, content, _ = match.groups()
        yield Subtitle(
            index=int(raw_index), start=srt_timestamp_to_timedelta(raw_start),
            end=srt_timestamp_to_timedelta(raw_end), content=content,
            proprietary=proprietary,
        )

    next_expected_start = 0
    for start, end in match_ranges:
        if start != next_expected_start:
            raise SRTParseError(
                'Expected to start at %d, but started at %d (content: %r)' % (
                    next_expected_start, start, srt[next_expected_start:start],
                )
            )

        next_expected_start = end

    if next_expected_start != len(srt):
        raise SRTParseError(
            'Expected to end at %d, but ended at %d (content: %r)' % (
                next_expected_start, len(srt), srt[next_expected_start:],
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
