#!/usr/bin/env python
# vim: set fileencoding=utf8
# pylint: disable=attribute-defined-outside-init

from __future__ import unicode_literals
import codecs
import tempfile
import srt
import os
from datetime import timedelta
from nose.tools import eq_ as eq, assert_not_equal as neq, assert_raises, \
                       assert_false, assert_true
from hypothesis import given, assume
import hypothesis.strategies as st
import zhon.cedict
import string
import functools


MIX_CHARS = ''.join([
    zhon.cedict.all,
    string.ascii_letters,
    string.digits,
    ' ',  # string.whitespace contains some funky shit that we don't care about
])
HOURS_IN_DAY = 24
TIMEDELTA_MAX_DAYS = 999999999
CONTENTLESS_SUB = functools.partial(
    srt.Subtitle, index=1,
    start=timedelta(seconds=1), end=timedelta(seconds=2),
)


@given(
    st.tuples(
        st.tuples(
            st.integers(min_value=0),
            st.integers(min_value=0),
            st.integers(min_value=0),
            st.text(alphabet=MIX_CHARS),
            st.text(min_size=1, alphabet=MIX_CHARS + '\n'),
        )
    )
)
def test_compose_and_parse_strict(raw_subs):
    input_subs = []

    for raw_sub in raw_subs:
        index, start_secs, end_secs, proprietary, content = raw_sub

        assume(content.strip())

        assume('\n' not in proprietary)
        assume('\n\n' not in content)

        input_subs.append(
            srt.Subtitle(
                index=index, start=timedelta(seconds=start_secs),
                end=timedelta(seconds=end_secs), proprietary=proprietary,
                content=content,
            )
        )
    composed = srt.compose(input_subs)
    reparsed_subs = srt.parse(composed)

    eq(
        [vars(sub) for sub in reparsed_subs],
        [vars(sub) for sub in input_subs],
    )


@given(st.text(min_size=1, alphabet=MIX_CHARS))
def test_compose_and_parse_strict_mode(content):
    content = '\n' + content + '\n\n' + content + '\n'
    sub = CONTENTLESS_SUB(content=content)

    parsed_strict = list(srt.parse(sub.to_srt()))[0]
    parsed_unstrict = list(srt.parse(sub.to_srt(strict=False)))[0]

    # Strict mode should remove blank lines in content, leading, and trailing
    # newlines.
    assert_false(parsed_strict.content.startswith('\n'))
    assert_false(parsed_strict.content.endswith('\n'))
    assert_false('\n\n' in parsed_strict.content)

    # When strict mode is false, no processing should be applied to the
    # content.
    assert_true(parsed_unstrict.content.startswith('\n'))
    assert_true(parsed_unstrict.content.endswith('\n'))
    assert_true('\n\n' in parsed_unstrict.content)


@given(st.integers(min_value=1, max_value=TIMEDELTA_MAX_DAYS))
def test_timedelta_to_srt_timestamp_can_go_over_24_hours(days):
    srt_timestamp = srt.timedelta_to_srt_timestamp(timedelta(days=days))
    srt_timestamp_hours = int(srt_timestamp.split(':')[0])
    eq(srt_timestamp_hours, days * HOURS_IN_DAY)


def test_subtitle_to_srt():
    sub = srt.Subtitle(
        index=1, start=srt.srt_timestamp_to_timedelta('00:01:02,003'),
        end=srt.srt_timestamp_to_timedelta('00:02:03,004'), content='foo',
    )
    eq(sub.to_srt(), '1\n00:01:02,003 --> 00:02:03,004\nfoo\n\n')

def test_timedelta_to_srt_timestamp():
    timedelta_ts = timedelta(
        hours=1, minutes=2, seconds=3, milliseconds=400,
    )
    eq(srt.timedelta_to_srt_timestamp(timedelta_ts), '01:02:03,400')

def test_srt_timestamp_to_timedelta():
    eq(
        timedelta(hours=1, minutes=2, seconds=3, milliseconds=400),
        srt.srt_timestamp_to_timedelta('01:02:03,400'),
    )

def test_subtitle_objects_hashable():
    hash(srt.Subtitle(
        index=1, start=srt.srt_timestamp_to_timedelta('00:01:02,003'),
        end=srt.srt_timestamp_to_timedelta('00:02:03,004'), content='foo',
    ))


class TestTinysrt(object):
    @staticmethod
    def _fixture(path):
        return os.path.join(os.path.dirname(__file__), path)

    @classmethod
    def setup_class(cls):
        cls.srt_filename = cls._fixture('srt_samples/monsters.srt')
        cls.srt_filename_windows = cls._fixture('srt_samples/monsters-win.srt')
        cls.srt_filename_bad_order = cls._fixture(
            'srt_samples/monsters-bad-order.srt'
        )
        cls.srt_filename_bad_newline = cls._fixture(
            'srt_samples/monsters-bad-newline.srt'
        )

        with codecs.open(cls.srt_filename, 'r', 'utf8') as srt_f:
            cls.srt_sample = srt_f.read()

        with codecs.open(cls.srt_filename_bad_order, 'r', 'utf8') as srt_bad_f:
            cls.srt_sample_bad_order = srt_bad_f.read()

        with codecs.open(cls.srt_filename_bad_newline, 'r', 'utf8') as srt_bad_f:
            cls.srt_sample_bad_newline = srt_bad_f.read()

    def setup(self):
        self.srt_f = codecs.open(self.srt_filename, 'r', 'utf8')
        self.srt_bad_order_f = codecs.open(
            self.srt_filename_bad_order, 'r', 'utf8'
        )
        self._temp_fd_bad_enc, self.temp_path = tempfile.mkstemp()
        os.close(self._temp_fd_bad_enc)
        self.temp_f = codecs.open(self.temp_path, 'w', 'utf8')

    def teardown(self):
        self.srt_f.close()
        self.srt_bad_order_f.close()
        self.temp_f.close()
        os.remove(self.temp_path)

    @staticmethod
    def _test_monsters_subs(subs, start_index=421):
        '''
        Test that monsters.srt was parsed correctly.
        '''
        subs = list(subs)

        eq(3, len(subs))

        eq(start_index, subs[0].index)
        eq(
            timedelta(
                hours=0,
                minutes=31,
                seconds=37,
                milliseconds=894,
            ),
            subs[0].start,
        )
        eq(
            timedelta(
                hours=0,
                minutes=31,
                seconds=39,
                milliseconds=928,
            ),
            subs[0].end,
        )
        eq(
            u'我有个点子\nOK, look, I think I have a plan here.',
            subs[0].content,
        )
        eq(
            u'hack the gibson',
            subs[0].proprietary,
        )

        eq(start_index + 1, subs[1].index)
        eq(
            timedelta(
                hours=0,
                minutes=31,
                seconds=39,
                milliseconds=931,
            ),
            subs[1].start,
        )
        eq(
            timedelta(
                hours=0,
                minutes=31,
                seconds=41,
                milliseconds=931,
            ),
            subs[1].end,
        )
        eq(
            u'我们要拿一堆汤匙\nUsing mainly spoons,',
            subs[1].content,
        )

    def test_subtitle_sort_by_start(self):
        subs = srt.parse(self.srt_sample_bad_order)
        sorted_subs = sorted(subs)

        eq(
            [x.index for x in sorted_subs],
            [422, 421, 423],
        )

    def test_subtitle_equality_false(self):
        subs_1 = list(srt.parse(self.srt_sample))
        subs_2 = list(srt.parse(self.srt_sample))
        subs_2[0].content += 'blah'

        neq(subs_1, subs_2)

    def test_subtitle_equality_true(self):
        subs_1 = list(srt.parse(self.srt_sample))
        subs_2 = list(srt.parse(self.srt_sample))
        eq(subs_1, subs_2)

    def test_parse(self):
        subs = list(srt.parse(self.srt_sample))
        self._test_monsters_subs(subs)

    def test_compose(self):
        subs = srt.parse(self.srt_sample)
        eq(self.srt_sample, srt.compose(subs, reindex=True, start_index=421))

    def test_sort_and_reindex_basic(self):
        subs = srt.parse(self.srt_sample_bad_order)
        sorted_and_reindexed_subs = srt.sort_and_reindex(subs, start_index=20)
        self._test_monsters_subs(sorted_and_reindexed_subs, start_index=20)

    def test_sar_skips_missing_content(self):
        subs = list(srt.parse(self.srt_sample))
        subs[1].content = '\n'
        sorted_and_reindexed_subs = srt.sort_and_reindex(subs, start_index=20)
        sorted_and_reindexed_subs = list(sorted_and_reindexed_subs)

        eq(2, len(sorted_and_reindexed_subs))
        eq(20, sorted_and_reindexed_subs[0].index)
        eq(21, sorted_and_reindexed_subs[1].index)
        eq(
            u'我有个点子\nOK, look, I think I have a plan here.',
            sorted_and_reindexed_subs[0].content,
        )
        eq(
            u'挖一条隧道 然后把她丢到野外去\n'
            'we dig a tunnel under the city and release it into the wild.',
            sorted_and_reindexed_subs[1].content,
        )

    def test_blank_line_without_index_continues_content(self):
        subs = list(srt.parse(self.srt_sample_bad_newline))
        eq(
            subs[0].content,
            '我有个点子\n\nOK, look, I think I have a plan here.',
        )
        eq(
            subs[1].content,
            '我们要拿一堆汤匙\n\nUsing mainly spoons,',
        )
        eq(
            subs[2].content,
            '挖一条隧道 然后把她丢到野外去\n\n'
            'we dig a tunnel under the city and release it into the wild.',
        )

    def test_to_srt_strict(self):
        srt_blocks = srt.compose(srt.parse(self.srt_sample_bad_newline))
        eq(srt_blocks.count('\n\n'), 3)

    def test_to_srt_unstrict(self):
        srt_blocks = srt.compose(
            srt.parse(self.srt_sample_bad_newline),
            strict=False,
        )
        eq(srt_blocks.count('\n\n'), 6)

    def test_parser_noncontiguous(self):
        unfinished_srt = '\n'.join(self.srt_sample.split('\n')[:-5]) + '\n'
        with assert_raises(srt.SRTParseError):
            list(srt.parse(unfinished_srt))
