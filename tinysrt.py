#!/usr/bin/env python

import re
import datetime
from collections import namedtuple

SUBTITLE_PATTERN = '(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.+?)\n\n'
SUBTITLE_REGEX = re.compile(SUBTITLE_PATTERN, re.MULTILINE | re.DOTALL)

Subtitle = namedtuple('Subtitle', ['index', 'start', 'end', 'content'])

def _timedelta_to_srt_timestamp(td):
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, milliseconds)

def parse_time(time):
    hours, minutes, seconds, milliseconds = map(int, re.split('[,:]', time))
    return datetime.timedelta(
        hours=hours, minutes=minutes,
        seconds=seconds, milliseconds=milliseconds,
    )


def parse(srt):
    # Pad the SRT to make sure the regex matches
    padded_srt = '\n%s\n' % srt

    for match in SUBTITLE_REGEX.finditer(padded_srt):
        raw_index, raw_start, raw_end, content = match.groups()
        yield Subtitle(
            index=int(raw_index), start=parse_time(raw_start),
            end=parse_time(raw_end), content=content,
        )

def create_srt(subtitles):
    output = ''
    for subtitle in subtitles:
        output += '%d\n%s --> %s\n%s\n\n' % (
            subtitle.index, _timedelta_to_srt_timestamp(subtitle.start),
            _timedelta_to_srt_timestamp(subtitle.end), subtitle.content,
        )
    return output
