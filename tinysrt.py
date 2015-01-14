#!/usr/bin/env python

'''A tiny library for parsing, modifying, and composing SRT files.'''

import re
import datetime
from collections import namedtuple

SUBTITLE_PATTERN = r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.+?)\n\n'
SUBTITLE_REGEX = re.compile(SUBTITLE_PATTERN, re.MULTILINE | re.DOTALL)

Subtitle = namedtuple('Subtitle', ['index', 'start', 'end', 'content'])


def timedelta_to_srt_timestamp(timedelta):
    '''Convert a timedelta to an SRT timestamp.'''

    hours, remainder = divmod(timedelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = timedelta.microseconds // 1000
    return '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, milliseconds)


def srt_timestamp_to_timedelta(srt_timestamp):
    '''Convert an SRT timestamp to a timedelta.'''

    split_time = [int(x) for x in re.split('[,:]', srt_timestamp)]
    hours, minutes, seconds, milliseconds = split_time
    return datetime.timedelta(
        hours=hours, minutes=minutes,
        seconds=seconds, milliseconds=milliseconds,
    )


def parse(srt):
    '''Convert an SRT formatted string into a generator of Subtitle objects.'''

    for match in SUBTITLE_REGEX.finditer(srt):
        raw_index, raw_start, raw_end, content = match.groups()
        yield Subtitle(
            index=int(raw_index), start=srt_timestamp_to_timedelta(raw_start),
            end=srt_timestamp_to_timedelta(raw_end), content=content,
        )


def compose(subtitles):
    '''Convert an interator of Subtitle objects to an SRT formatted string.'''

    srt = []
    for subtitle in subtitles:
        srt.append('%d\n%s --> %s\n%s\n\n' % (
            subtitle.index, timedelta_to_srt_timestamp(subtitle.start),
            timedelta_to_srt_timestamp(subtitle.end), subtitle.content,
        ))
    return ''.join(srt)
