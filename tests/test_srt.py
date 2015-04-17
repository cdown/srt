#!/usr/bin/env python
# vim: set fileencoding=utf8

import codecs
import tempfile
import srt
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
        cls.srt_filename_windows = cls._fixture('srt_samples/monsters-win.srt')
        cls.srt_filename_bad_order = cls._fixture(
            'srt_samples/monsters-bad-order.srt'
        )

        with codecs.open(cls.srt_filename, 'r', 'utf8') as srt_f:
            cls.srt_sample = srt_f.read()

        with codecs.open(cls.srt_filename_bad_order, 'r', 'utf8') as srt_bad_f:
            cls.srt_sample_bad_order = srt_bad_f.read()

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

        This is in its own function since these tests are used both when
        testing srt.parse and srt.parse_file.
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
            u' hack the gibson',
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

    @staticmethod
    def test_subtitle_to_srt():
        sub = srt.Subtitle(
            index=1, start=srt.srt_timestamp_to_timedelta('00:01:02,003'),
            end=srt.srt_timestamp_to_timedelta('00:02:03,004'), content='foo',
        )
        eq(sub.to_srt(), '1\n00:01:02,003 --> 00:02:03,004\nfoo\n\n')

    @staticmethod
    def test_timedelta_to_srt_timestamp():
        timedelta_ts = timedelta(
                hours=1, minutes=2, seconds=3, milliseconds=400,
        )
        eq(srt.timedelta_to_srt_timestamp(timedelta_ts), '01:02:03,400')

    @staticmethod
    def test_srt_timestamp_to_timedelta():
        eq(
            timedelta(hours=1, minutes=2, seconds=3, milliseconds=400),
            srt.srt_timestamp_to_timedelta('01:02:03,400'),
        )

    def test_parse(self):
        subs = list(srt.parse(self.srt_sample))
        self._test_monsters_subs(subs)

    def test_parse_file(self):
        srt_f = codecs.open(self.srt_filename, 'r', 'utf8')
        subs = list(srt.parse_file(srt_f))
        self._test_monsters_subs(subs)
        srt_f.close()

    def test_parse_file_windows(self):
        srt_f = codecs.open(self.srt_filename_windows, 'r', 'utf8')
        subs = list(srt.parse_file(srt_f))
        self._test_monsters_subs(subs)
        srt_f.close()

    def test_compose(self):
        subs = srt.parse(self.srt_sample)
        eq(self.srt_sample, srt.compose(subs, reindex=True, start_index=421))

    def test_compose_file(self):
        srt_in_f = codecs.open(self.srt_filename, 'r', 'utf8')
        srt_out_f = self.temp_f

        subs = srt.parse_file(srt_in_f)
        srt.compose_file(subs, srt_out_f, reindex=False)

        srt_in_f.seek(0)

        srt_out_f.close()
        srt_out_f_2 = codecs.open(self.temp_path, 'r', 'utf8')

        eq(srt_in_f.read(), srt_out_f_2.read())

        srt_in_f.close()
        srt_out_f_2.close()

    def test_compose_file_num(self):
        srt_in_f = codecs.open(self.srt_filename, 'r', 'utf8')
        srt_out_f = self.temp_f

        subs = srt.parse_file(srt_in_f)
        num_written = srt.compose_file(subs, srt_out_f)

        eq(3, num_written)

        srt_in_f.close()

    def test_compose_file_num_none(self):
        srt_out_f = self.temp_f

        subs = list(srt.parse(''))
        num_written = srt.compose_file(subs, srt_out_f)

        eq(0, num_written)

    @staticmethod
    def test_subtitle_objects_hashable():
        hash(srt.Subtitle(
            index=1, start=srt.srt_timestamp_to_timedelta('00:01:02,003'),
            end=srt.srt_timestamp_to_timedelta('00:02:03,004'), content='foo',
        ))

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
