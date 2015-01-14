#!/usr/bin/env python
# vim: set fileencoding=utf8

import textwrap
import tinysrt
import datetime
from nose.tools import eq_ as eq

def test_timedelta_to_srt_timestamp():
    dt = datetime.timedelta(hours=1, minutes=2, seconds=3, milliseconds=400)
    eq(tinysrt.timedelta_to_srt_timestamp(dt), '01:02:03,400')

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
        我快要渴死了
        快点倒酒!

        8
        00:01:56,480 --> 00:01:58,460
        - 给你  - 谢了
        '''
    )
    subs = list(tinysrt.parse(srt_data))

    eq(2, len(subs))

    eq(7, subs[0].index)
    eq(
        datetime.timedelta(
            hours=0,
            minutes=1,
            seconds=51,
            milliseconds=980,
        ),
        subs[0].start,
    )
    eq(
        datetime.timedelta(
            hours=0,
            minutes=1,
            seconds=55,
            milliseconds=910,
        ),
        subs[0].end,
    )
    eq(
        '我快要渴死了\n快点倒酒!',
        subs[0].content,
    )

    eq(8, subs[1].index)
    eq(
        datetime.timedelta(
            hours=0,
            minutes=1,
            seconds=56,
            milliseconds=480,
        ),
        subs[1].start,
    )
    eq(
        datetime.timedelta(
            hours=0,
            minutes=1,
            seconds=58,
            milliseconds=460,
        ),
        subs[1].end,
    )
    eq(
        '- 给你  - 谢了',
        subs[1].content,
    )

def test_compose():
    srt_data = textwrap.dedent(
        '''\
        203
        00:32:47,312 --> 00:32:53,239
        蛋表面有一层薄膜，一碰就有反应

        204
        00:32:57,088 --> 00:33:00,012
        肯恩，你没事吧？

        '''
    )
    subs = tinysrt.parse(srt_data)
    eq(srt_data, tinysrt.compose(subs))
