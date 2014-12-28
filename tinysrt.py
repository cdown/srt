#!/usr/bin/env python

import re
import datetime
from collections import namedtuple

SUBTITLE_REGEX = re.compile(r'''\
(\d+)
(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)
(.+)
''')

Subtitle = namedtuple('Subtitle', ['index', 'start', 'end', 'content'])


def parse_time(time):
    hours, minutes, seconds, milliseconds = map(int, re.split('[,:]', time))
    return datetime.timedelta(
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        milliseconds=milliseconds,
    )


def parse(srt):
    for match in SUBTITLE_REGEX.finditer(srt):
        raw_index, raw_start, raw_end, content = match.groups()
        yield Subtitle(
            index=int(raw_index), start=parse_time(raw_start),
            end=parse_time(raw_end), content=content,
        )
