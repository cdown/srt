#!/usr/bin/env python

'''A tiny library for parsing, modifying, and composing SRT files.'''

import functools
import re
from datetime import timedelta


SUBTITLE_PATTERN = r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.+?)\n\n'
SUBTITLE_REGEX = re.compile(SUBTITLE_PATTERN, re.MULTILINE | re.DOTALL)


@functools.total_ordering
class Subtitle(object):
    def __init__(self, index, start, end, content):
        self.index = index
        self.start = start
        self.end = end
        self.content = content

    def __eq__(self, other): return self.__dict__ == other.__dict__
    def __lt__(self, other): return self.start < other.start


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


def parse_stream(srt_stream, sub_buf_size=512):
    '''
    Parse an SRT formatted stream into Subtitle objects in a
    memory-efficient way.
    '''
    current_sub = 0
    sub_buf = ''
    last_flushed = 0

    for line in srt_stream:
        sub_buf += line
        if line == '\n' and last_flushed + sub_buf_size > current_sub:
            for subtitle in parse(sub_buf):
                yield subtitle
            last_flushed = current_sub
            sub_buf = ''

    for subtitle in parse(sub_buf):
        yield subtitle


def compose(subtitles):
    '''Convert an iterator of Subtitle objects to an SRT formatted string.'''
    srt = []
    for subtitle in subtitles:
        srt.append('%d\n%s --> %s\n%s\n\n' % (
            subtitle.index, timedelta_to_srt_timestamp(subtitle.start),
            timedelta_to_srt_timestamp(subtitle.end), subtitle.content,
        ))
    return ''.join(srt)


def reindex(subtitles):
    '''
    Fix erroneously indexed subtitles so that they are displayed in time order
    with the correct index.
    '''
    for index, subtitle in enumerate(sorted(subtitles), start=1):
        subtitle.index = index
        yield subtitle
