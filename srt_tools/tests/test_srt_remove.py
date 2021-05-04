import unittest

import srt
from srt import srt_timestamp_to_timedelta as t
### TODO: Need to import srt_remove


def create_blocks(setting=0):
    """Creates a generator of subtitles for testing purposes"""
    subs = []
    if setting == 0:
        subs.append(srt.Subtitle(1, t('00:00:11,000'), t('00:00:12,701'), "A"))
        subs.append(srt.Subtitle(2, t('00:00:12,701'), t('00:00:14,203'), "B"))
        subs.append(srt.Subtitle(3, t('00:00:14,500'), t('00:00:19,738'), "C"))
        subs.append(srt.Subtitle(4, t('00:00:16,538'), t('00:00:17,272'), "D"))
        subs.append(srt.Subtitle(5, t('00:00:17,272'), t('00:00:18,440'), "E"))
    elif setting == 1:
        subs.append(srt.Subtitle(1, t('00:00:1,000'), t('00:00:10,000'), "A"))
        subs.append(srt.Subtitle(2, t('00:00:2,000'), t('00:00:08,000'), "B"))
        subs.append(srt.Subtitle(3, t('00:00:3,000'), t('00:00:05,000'), "C"))
        subs.append(srt.Subtitle(4, t('00:00:3,500'), t('00:00:04,500'), "D"))
        subs.append(srt.Subtitle(5, t('00:00:6,000'), t('00:00:08,000'), "E"))
        subs.append(srt.Subtitle(6, t('00:00:9,000'), t('00:00:10,000'), "F"))

    for subtitle in subs:
        yield subtitle


def sort(subs):
    return list(srt.sort_and_reindex(subs))


class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.subs = create_blocks
        self.x = list(create_blocks())
        self.y = list(create_blocks(1))
        self.r = self.x[0]

    def tearDown(self):
        pass

    def test_get_timestamp(self):
        # Indexes
        self.assertEqual(get_timestamp(self.subs(), 0), self.x[0].start)
        self.assertEqual(get_timestamp(self.subs(), 4), self.x[4].start)
        self.assertEqual(get_timestamp(self.subs(), -1), self.x[-1].start)
        self.assertEqual(get_timestamp(self.subs(), -4), self.x[-4].start)
        self.assertEqual(get_timestamp(self.subs(), -5), self.x[0].start)
        with self.assertRaises(IndexError):
            get_timestamp(self.subs(), 5)
            get_timestamp(self.subs(), -6)

        # Strings
        self.assertEqual(get_timestamp(
            self.subs(), t('00:00:11,000')), self.x[0].start)
        self.assertEqual(get_timestamp(
            self.subs(), t('00:00:0,000')), t('00:00:0,000'))
        self.assertEqual(get_timestamp(
            self.subs(), t('00:00:30,000')), t('00:00:30,000'))
        with self.assertRaises(srt.TimestampParseError):
            self.assertEqual(get_timestamp(self.subs(), t('-00:00:50,000')))
            self.assertEqual(get_timestamp(self.subs(), t('00:00:-10,000')))

        # Date Time
        self.assertEqual(get_timestamp(
            self.subs(), t('00:00:11,000')), self.x[0].start)

    def test_contains_timestamp(self):
        self.assertEqual(contains_timestamp(self.r, t('00:00:10,000')), False)
        self.assertEqual(contains_timestamp(
            self.r, t('00:00:11,000')), True)  # start
        self.assertEqual(contains_timestamp(
            self.r, t('00:00:12,000')), True)  # btwn
        self.assertEqual(contains_timestamp(
            self.r, t('00:00:12,701')), False)  # end
        self.assertEqual(contains_timestamp(self.r, t('00:00:13,000')), False)

    def test_captions_containing_timestamp(self):
        self.assertEqual(captions_containing_timestamp(
            self.subs(), t('00:00:00,000')), [])
        self.assertEqual(captions_containing_timestamp(
            self.subs(), t('00:00:11,000')), [self.x[0]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(), t('00:00:12,000')), [self.x[0]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(), t('00:00:12,701')), [self.x[1]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(), t('00:00:35,000')), [])
        self.assertEqual(captions_containing_timestamp(
            self.subs(), t('00:00:16,708')), [self.x[2], self.x[3]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(), t('00:00:17,272')), [self.x[2], self.x[4]])

        # distanced overlaps
        self.assertEqual(captions_containing_timestamp(self.subs(1), t(
            '00:00:4,000')), [self.y[0], self.y[1], self.y[2], self.y[3]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(1), t('00:00:9,000')), [self.y[0], self.y[5]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(1), t('00:00:9,500')), [self.y[0], self.y[5]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(1), t('00:00:3,450')), [self.y[0], self.y[1], self.y[2]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(1), t('00:00:5,500')), [self.y[0], self.y[1]])
        self.assertEqual(captions_containing_timestamp(
            self.subs(1), t('00:00:11,000')), [])


class TestCaptionTools(unittest.TestCase):
    def setUp(self):
        self.subs = create_blocks
        self.x = list(create_blocks())
        self.y = list(create_blocks(1))

    def tearDown(self):
        pass

    def test_remove_caption_index(self):
        a = sort([self.x[0], self.x[2], self.x[3], self.x[4]])

        result = remove_caption_index(self.subs(), 1, 2)
        self.assertEqual(list(result), a)

        result = remove_caption_index(self.subs(), 1, -3)
        self.assertEqual(list(result), a)

        result = remove_caption_index(self.subs(), 1, 3)
        self.assertEqual(list(result), sort([self.x[0], self.x[3], self.x[4]]))

        result = remove_caption_index(self.subs(), 2, 5)
        self.assertEqual(list(result), sort([self.x[0], self.x[1]]))

        result = remove_caption_index(self.subs(), -2, 3)
        self.assertEqual(list(result), [])
        with self.assertRaises(IndexError):
            result = list(remove_caption_index((y for y in []), 0, 1))
            result = list(remove_caption_index(self.subs(), 1, 8))
            result = list(remove_caption_index(self.subs(), -7, 4))
            result = list(remove_caption_index(self.subs(), 5, 4))

        result = remove_caption_index(self.subs(), 3, 1)  # reverse
        self.assertEqual(list(result), sort([self.x[1], self.x[2]]))

        result = remove_caption_index(self.subs(), 2, 0)  # reverse
        self.assertEqual(list(result), sort([self.x[0], self.x[1]]))

        a = sort([self.x[2], self.x[3]])

        result = remove_caption_index(self.subs(), -1, -3)  # reverse
        self.assertEqual(list(result), a)

        result = remove_caption_index(self.subs(), 4, 2)  # reverse
        self.assertEqual(list(result), a)

        # single parameter
        result = remove_caption_index(self.subs(), 0)
        self.assertEqual(list(result), [])

        result = remove_caption_index(self.subs(), 2)
        self.assertEqual(list(result), sort([self.x[0], self.x[1]]))

    def test_remove_caption_timestamp(self):
        result = remove_caption_timestamp(
            [], t('00:00:00,000'), t('00:00:30,000'))
        self.assertEqual(list(result), [])

        result = remove_caption_timestamp(
            self.subs(), self.x[0].start, self.x[0].end)
        self.assertEqual(list(result), sort(
            [self.x[1], self.x[2], self.x[3], self.x[4]]))

        result = remove_caption_timestamp(
            self.subs(), self.x[0].start, t('00:00:14,500'))
        self.assertEqual(list(result), sort([self.x[2], self.x[3], self.x[4]]))

        result = remove_caption_timestamp(
            self.subs(), t('00:00:11,000'), t('00:00:19,738'))
        self.assertEqual(list(result), [])

        result = remove_caption_timestamp(
            self.subs(), t('00:00:00,000'), t('00:00:30,000'))
        self.assertEqual(list(result), [])

        result = remove_caption_timestamp(
            self.subs(), t('00:00:00,000'), t('00:00:17,500'))
        a = [srt.Subtitle(1, t('00:00:17,500'), t('00:00:18,440'), "E"),
             srt.Subtitle(2, t('00:00:17,500'), t('00:00:19,738'), "C")]
        self.assertEqual(list(result), a)  # split

        # reverse timestamps
        result = remove_caption_timestamp(
            [], t('00:00:30,000'), t('00:00:00,000'))
        self.assertEqual(list(result), [])

        result = remove_caption_timestamp(
            self.subs(), t('00:00:30,000'), t('00:00:00,000'))
        self.assertEqual(list(result), self.x)

        result = remove_caption_timestamp(
            self.subs(), t('00:00:14,500'), self.x[0].start)
        self.assertEqual(list(result), sort([self.x[0], self.x[1]]))

        result = remove_caption_timestamp(
            self.subs(), t('00:00:19,738'), t('00:00:11,000'))
        self.assertEqual(list(result), self.x)

        result = remove_caption_timestamp(
            self.subs(), self.x[0].end, self.x[0].start)
        self.assertEqual(list(result), [self.x[0]])

        result = remove_caption_timestamp(
            self.subs(), self.x[0].start, self.x[0].start)
        self.assertEqual(list(result), [])


if __name__ == '__main__':
    unittest.main()
