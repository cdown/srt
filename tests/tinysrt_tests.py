#!/usr/bin/env python
# vim: set fileencoding=utf8

import textwrap
import tinysrt
from datetime import timedelta
from nose.tools import eq_ as eq, assert_not_equal as neq

def test_timedelta_to_srt_timestamp():
    timedelta_ts = timedelta(hours=1, minutes=2, seconds=3, milliseconds=400)
    eq(tinysrt.timedelta_to_srt_timestamp(timedelta_ts), '01:02:03,400')

def test_srt_timestamp_to_timedelta():
    eq(
        timedelta(hours=1, minutes=2, seconds=3, milliseconds=400),
        tinysrt.srt_timestamp_to_timedelta('01:02:03,400'),
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
        timedelta(
            hours=0,
            minutes=1,
            seconds=51,
            milliseconds=980,
        ),
        subs[0].start,
    )
    eq(
        timedelta(
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
        timedelta(
            hours=0,
            minutes=1,
            seconds=56,
            milliseconds=480,
        ),
        subs[1].start,
    )
    eq(
        timedelta(
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


def test_default_subtitle_sorting_is_by_start_time():
    srt_data = textwrap.dedent(
        '''\
        421
        00:31:39,931 --> 00:31:41,931
        我们要拿一堆汤匙

        422
        00:31:37,894 --> 00:31:39,928
        我有个点子

        423
        00:31:41,933 --> 00:31:43,435
        挖一条隧道 然后把她丢到野外去

        '''
    )

    subs = tinysrt.parse(srt_data)
    sorted_subs = sorted(subs)

    eq(
        [x.index for x in sorted_subs],
        [422, 421, 423],
    )


def test_subtitle_equality_false():
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

    subs_1 = list(tinysrt.parse(srt_data))
    subs_2 = list(tinysrt.parse(srt_data))
    subs_2[0].content += 'blah'

    neq(subs_1, subs_2)


def test_subtitle_equality_true():
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
    subs_1 = list(tinysrt.parse(srt_data))
    subs_2 = list(tinysrt.parse(srt_data))
    eq(subs_1, subs_2)

def test_fix_indexing():
    srt_data = textwrap.dedent(
        '''\
        421
        00:31:39,931 --> 00:31:41,931
        我们要拿一堆汤匙

        422
        00:31:37,894 --> 00:31:39,928
        我有个点子

        423
        00:31:41,933 --> 00:31:43,435
        挖一条隧道 然后把她丢到野外去

        '''
    )

    subs = tinysrt.parse(srt_data)
    reindexed_subs = tinysrt.reindex(subs)

    expected = textwrap.dedent(
        '''\
        1
        00:31:37,894 --> 00:31:39,928
        我有个点子

        2
        00:31:39,931 --> 00:31:41,931
        我们要拿一堆汤匙

        3
        00:31:41,933 --> 00:31:43,435
        挖一条隧道 然后把她丢到野外去

        '''
    )

    eq(expected, tinysrt.compose(reindexed_subs))
