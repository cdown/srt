#!/usr/bin/env python

'''A tiny library for parsing, modifying, and composing SRT files.'''

import functools
import re
from datetime import timedelta
from itertools import groupby


SUBTITLE_PATTERN = r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.+?)\n\n'
SUBTITLE_REGEX = re.compile(SUBTITLE_PATTERN, re.MULTILINE | re.DOTALL)


@functools.total_ordering
class Subtitle(object):
    def __init__(self, index, start, end, content):
        self.index = index
        self.start = start
        self.end = end
        self.content = content

    def __str__(self):
        return '%d\n%s --> %s\n%s\n\n' % (
            self.index, timedelta_to_srt_timestamp(self.start),
            timedelta_to_srt_timestamp(self.end), self.content,
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return self.start < other.start


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


def parse_stream(srt_stream):
    '''
    Parse an SRT formatted stream into Subtitle objects in a
    memory-efficient way.
    '''
    for is_sep, lines in groupby(srt_stream, lambda line: line != '\n'):
        if is_sep:
            srt_block = ''.join(lines) + '\n'
            subtitle, = parse(srt_block)
            yield subtitle


def compose(subtitles):
    '''Convert an iterator of Subtitle objects to an SRT formatted string.'''
    return (str(subtitle) for subtitle in subtitles)


def reindex(subtitles):
    '''Order all subtitles by start time and rewrite their indexes from 1.'''
    for index, subtitle in enumerate(sorted(subtitles), start=1):
        subtitle.index = index
        yield subtitle
