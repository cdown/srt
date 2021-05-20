import unittest
import srt
from srt import srt_timestamp_to_timedelta as t

# import srt-remove as a source file.
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader
import os
folder_path = os.path.normpath(os.path.join(
                os.path.normpath(os.path.join(__file__, os.pardir)), os.pardir))
file_path = os.path.normpath(os.path.join(folder_path, 'srt-remove'))
spec = spec_from_loader("srt-remove", SourceFileLoader("srt-remove", file_path))
module = module_from_spec(spec)
spec.loader.exec_module(module)

# emulate `from module import *`
if "__all__" in module.__dict__:
    names = module.__dict__["__all__"]
else:
    names = [x for x in module.__dict__ if not x.startswith("_")]

globals().update({k: getattr(module, k) for k in names})


# helper methods
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


class TestCaptionTools(unittest.TestCase):
    def setUp(self):
        self.subs = create_blocks
        self.x = list(create_blocks())
        self.y = list(create_blocks(1))

    def tearDown(self):
        pass

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

    def test_split(self):
        a = [srt.Subtitle(1, t('00:00:11,000'), t('00:00:12,701'), "A"),
             srt.Subtitle(2, t('00:00:12,701'), t('00:00:14,203'), "B"),
             srt.Subtitle(3, t('00:00:14,500'), t('00:00:17,500'), "C"),
             srt.Subtitle(4, t('00:00:16,538'), t('00:00:17,272'), "D"),
             srt.Subtitle(5, t('00:00:17,272'), t('00:00:17,500'), "E"),
             srt.Subtitle(6, t('00:00:17,500'), t('00:00:18,440'), "E"),
             srt.Subtitle(7, t('00:00:17,500'), t('00:00:19,738'), "C")]
        result = split(self.subs(),  t('00:00:17,500'))
        self.assertEqual(list(result), a)

        result = split(self.subs(), self.x[0].start)
        self.assertEqual(list(result), self.x)



if __name__ == '__main__':
    unittest.main()
