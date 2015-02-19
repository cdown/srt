#!/usr/bin/env python

'''A tiny library for parsing, modifying, and composing SRT files.'''

import functools
import re
from datetime import timedelta
from collections import namedtuple

SUBTITLE_PATTERN = r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.+?)\n\n'
SUBTITLE_REGEX = re.compile(SUBTITLE_PATTERN, re.MULTILINE | re.DOTALL)


@functools.total_ordering
class _SubtitleSorting(object):
    def __eq__(self, other): return self.start == other.start
    def __lt__(self, other): return self.start <  other.start


class Subtitle(_SubtitleSorting,
               namedtuple('Subtitle', ['index', 'start', 'end', 'content'])):
    pass


def timedelta_to_srt_timestamp(timedelta_timestamp):
    '''Convert a timedelta to an SRT timestamp.'''
    hrs, remainder = divmod(timedelta_timestamp.seconds, 3600)
    mins, secs = divmod(remainder, 60)
    msecs = timedelta_timestamp.microseconds // 1000
    return '%02d:%02d:%02d,%03d' % (hrs, mins, secs, msecs)


def srt_timestamp_to_timedelta(srt_timestamp):
    '''Convert an SRT timestamp to a timedelta.'''
    hrs, mins, secs, msecs = map(int, re.split('[,:]', srt_timestamp))
    return timedelta(hours=hrs, minutes=mins, seconds=secs, milliseconds=msecs)


def parse(srt):
    '''Convert an SRT formatted string to a generator of Subtitle objects.'''
    for match in SUBTITLE_REGEX.finditer(srt):
        raw_index, raw_start, raw_end, content = match.groups()
        yield Subtitle(
            index=int(raw_index), start=srt_timestamp_to_timedelta(raw_start),
            end=srt_timestamp_to_timedelta(raw_end), content=content,
        )


def compose(subtitles):
    '''Convert an iterator of Subtitle objects to an SRT formatted string.'''
    srt = []
    for subtitle in subtitles:
        srt.append('%d\n%s --> %s\n%s\n\n' % (
            subtitle.index, timedelta_to_srt_timestamp(subtitle.start),
            timedelta_to_srt_timestamp(subtitle.end), subtitle.content,
        ))
    return ''.join(srt)
