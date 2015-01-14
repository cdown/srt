#!/usr/bin/env python

'''
A tiny library for manipulating back and forth from SRT to Python objects.
'''

import re
import datetime
from collections import namedtuple

SUBTITLE_PATTERN = r'(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.+?)\n\n'
SUBTITLE_REGEX = re.compile(SUBTITLE_PATTERN, re.MULTILINE | re.DOTALL)

Subtitle = namedtuple('Subtitle', ['index', 'start', 'end', 'content'])


def timedelta_to_srt_timestamp(timedelta):
    '''
    Convert a datetime.timedelta object to a SRT formatted timestamp.
    '''

    hours, remainder = divmod(timedelta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = timedelta.microseconds // 1000
    return '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, milliseconds)


def parse_time(time):
    '''
    Parse an SRT formatted time to HH:MM:SS,ms.
    '''

    split_time = [int(x) for x in re.split('[,:]', time)]
    hours, minutes, seconds, milliseconds = split_time
    return datetime.timedelta(
        hours=hours, minutes=minutes,
        seconds=seconds, milliseconds=milliseconds,
    )


def parse(srt):
    '''
    Parse an SRT formatted string into Subtitle objects.
    '''

    # Pad the SRT to make sure the regex matches
    padded_srt = '\n%s\n' % srt

    for match in SUBTITLE_REGEX.finditer(padded_srt):
        raw_index, raw_start, raw_end, content = match.groups()
        yield Subtitle(
            index=int(raw_index), start=parse_time(raw_start),
            end=parse_time(raw_end), content=content,
        )


def compose(subtitles):
    '''
    Create an SRT from an iterator of Subtitle objects (such as that returned
    from parse()).
    '''

    output = ''
    for subtitle in subtitles:
        output += '%d\n%s --> %s\n%s\n\n' % (
            subtitle.index, timedelta_to_srt_timestamp(subtitle.start),
            timedelta_to_srt_timestamp(subtitle.end), subtitle.content,
        )
    return output
