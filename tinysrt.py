#!/usr/bin/env python

import re
import datetime
from collections import namedtuple

SUBTITLE_PATTERN = '(\d+)\n(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.+?)\n\n'
SUBTITLE_REGEX = re.compile(SUBTITLE_PATTERN, re.MULTILINE | re.DOTALL)

Subtitle = namedtuple('Subtitle', ['index', 'start', 'end', 'content'])


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
