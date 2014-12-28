#!/usr/bin/env python
# vim: set fileencoding=utf8

import textwrap
import tinysrt
import datetime
from nose.tools import eq_ as eq


def test_parse_time():
    eq(
        datetime.timedelta(hours=1, minutes=2, seconds=3, milliseconds=400),
        tinysrt.parse_time('01:02:03,400'),
    )

def test_parse_general():
    srt_data = textwrap.dedent(
        '''\
        7
        00:01:51,980 --> 00:01:55,910
        我快要渴死了 快点倒酒!

        '''
    )
    subs = list(tinysrt.parse(srt_data))

    eq(1, len(subs))

    sub = subs[0]

    eq(7, sub.index)
    eq(
        datetime.timedelta(
            hours=0,
            minutes=1,
            seconds=51,
            milliseconds=980,
        ),
        sub.start,
    )
    eq(
        datetime.timedelta(
            hours=0,
            minutes=1,
            seconds=55,
            milliseconds=910,
        ),
        sub.end,
    )
    eq(
        '我快要渴死了 快点倒酒!',
        sub.content,
    )
