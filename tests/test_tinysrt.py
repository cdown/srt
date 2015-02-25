#!/usr/bin/env python
# vim: set fileencoding=utf8

import tempfile
import tinysrt
import os
from datetime import timedelta
from nose.tools import eq_ as eq, assert_not_equal as neq


class TestTinysrt(object):
    @staticmethod
    def _fixture(path):
        return os.path.join(os.path.dirname(__file__), path)

    @classmethod
    def setup_class(cls):
        cls.srt_filename = cls._fixture('srt_samples/monsters.srt')
        cls.srt_filename_bad_order = cls._fixture(
            'srt_samples/monsters-bad-order.srt'
        )

        with open(cls.srt_filename) as srt_f:
            cls.srt_sample = srt_f.read()

        with open(cls.srt_filename_bad_order) as srt_bad_f:
            cls.srt_sample_bad_order = srt_bad_f.read()

    def setup(self):
        self.srt_f = open(self.srt_filename)
        self.srt_bad_order_f = open(self.srt_filename_bad_order)
        self.temp_fd, self.temp_path = tempfile.mkstemp()
        self.temp_f = os.fdopen(self.temp_fd, 'w')

    def teardown(self):
        self.srt_f.close()
        self.srt_bad_order_f.close()
        self.temp_f.close()
        os.remove(self.temp_path)

    @staticmethod
    def test_timedelta_to_srt_timestamp():
        timedelta_ts = timedelta(
                hours=1, minutes=2, seconds=3, milliseconds=400,
        )
        eq(tinysrt.timedelta_to_srt_timestamp(timedelta_ts), '01:02:03,400')

    @staticmethod
    def test_srt_timestamp_to_timedelta():
        eq(
            timedelta(hours=1, minutes=2, seconds=3, milliseconds=400),
            tinysrt.srt_timestamp_to_timedelta('01:02:03,400'),
        )

    @staticmethod
    def _test_monsters_subs(subs):
        eq(3, len(subs))

        eq(421, subs[0].index)
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
            '我有个点子\nOK, look, I think I have a plan here.',
            subs[0].content,
        )

        eq(422, subs[1].index)
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
            '我们要拿一堆汤匙\nUsing mainly spoons,',
            subs[1].content,
        )

    def test_parse_general(self):
        subs = list(tinysrt.parse(self.srt_sample))
        self._test_monsters_subs(subs)

    def test_parse_file(self):
        srt_f = open(self.srt_filename)
        subs = list(tinysrt.parse_file(srt_f))
        self._test_monsters_subs(subs)
        srt_f.close()

    def test_compose(self):
        subs = tinysrt.parse(self.srt_sample)
        eq(self.srt_sample, tinysrt.compose(subs))

    def test_subtitle_sort_by_start(self):
        subs = tinysrt.parse(self.srt_sample_bad_order)
        sorted_subs = sorted(subs)

        eq(
            [x.index for x in sorted_subs],
            [422, 421, 423],
        )

    def test_subtitle_equality_false(self):
        subs_1 = list(tinysrt.parse(self.srt_sample))
        subs_2 = list(tinysrt.parse(self.srt_sample))
        subs_2[0].content += 'blah'

        neq(subs_1, subs_2)

    def test_subtitle_equality_true(self):
        subs_1 = list(tinysrt.parse(self.srt_sample))
        subs_2 = list(tinysrt.parse(self.srt_sample))
        eq(subs_1, subs_2)

    def test_compose_file(self):
        srt_in_f = open(self.srt_filename)
        srt_out_f = self.temp_f

        subs = tinysrt.parse_file(srt_in_f)
        tinysrt.compose_file(subs, srt_out_f)

        srt_in_f.seek(0)

        srt_out_f.close()
        srt_out_f_2 = open(self.temp_path)

        eq(srt_in_f.read(), srt_out_f_2.read())

        srt_in_f.close()
        srt_out_f_2.close()

    def test_compose_file_num(self):
        srt_in_f = open(self.srt_filename)
        srt_out_f = self.temp_f

        subs = tinysrt.parse_file(srt_in_f)
        num_written = tinysrt.compose_file(subs, srt_out_f)

        eq(3, num_written)

        srt_in_f.close()

    def test_compose_file_num_none(self):
        srt_out_f = self.temp_f

        subs = list(tinysrt.parse(''))
        num_written = tinysrt.compose_file(subs, srt_out_f)

        eq(0, num_written)
