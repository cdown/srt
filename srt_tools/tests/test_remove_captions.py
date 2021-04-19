# import unittest
# import importlib
# import srt
# from srt import srt_timestamp_to_timedelta as t
#
# def sort(subs):
#     return list(srt.sort_and_reindex(subs))
#
# def create_blocks(setting=0):
#     subs = []
#     if setting == 0:
#         subs.append(srt.Subtitle(1, t('00:00:11,000'), t('00:00:12,701'), "A"))
#         subs.append(srt.Subtitle(2, t('00:00:12,701'), t('00:00:14,203'), "B"))
#         subs.append(srt.Subtitle(3, t('00:00:14,500'), t('00:00:19,738'), "C"))
#         subs.append(srt.Subtitle(4, t('00:00:16,538'), t('00:00:17,272'), "D"))
#         subs.append(srt.Subtitle(5, t('00:00:17,272'), t('00:00:18,440'), "E"))
#     elif setting == 1:
#         subs.append(srt.Subtitle(1, t('00:00:1,000'), t('00:00:10,000'), "A"))
#         subs.append(srt.Subtitle(2, t('00:00:2,000'), t('00:00:08,000'), "B"))
#         subs.append(srt.Subtitle(3, t('00:00:3,000'), t('00:00:05,000'), "C"))
#         subs.append(srt.Subtitle(4, t('00:00:3,500'), t('00:00:04,500'), "D"))
#         subs.append(srt.Subtitle(5, t('00:00:6,000'), t('00:00:08,000'), "E"))
#         subs.append(srt.Subtitle(6, t('00:00:9,000'), t('00:00:10,000'), "F"))
#     return subs
#
# from srt_tools.utils import *
# srt_remove = importlib.import_module('srt-remove')
# from srt_remove import *
#
# class TestRemoveCaptions(unittest.TestCase):
#     def setUp(self):
#         self.subs = create_blocks()
#
#     def tearDown(self):
#         pass
#
#     def test_get_timestamp(self):
#         # Indexes
#         self.assertEqual(get_timestamp(self.subs, 0), self.subs[0].start)
#         self.assertEqual(get_timestamp(self.subs, 4), self.subs[4].start)
#         self.assertEqual(get_timestamp(self.subs, -1), self.subs[-1].start)
#         self.assertEqual(get_timestamp(self.subs, -4), self.subs[-4].start)
#         with self.assertRaises(IndexError):
#             get_timestamp(self.subs, -5)
#
#         # Strings
#         self.assertEqual(get_timestamp(self.subs, '00:00:11,000'), self.subs[0].start)
#         self.assertEqual(get_timestamp(self.subs, '00:00:0,000'), t('00:00:0,000'))
#         self.assertEqual(get_timestamp(self.subs, '00:00:30,000'), t('00:00:30,000'))
#         with self.assertRaises(srt.TimestampParseError):
#             self.assertEqual(get_timestamp(self.subs, '-00:00:50,000'))
#             self.assertEqual(get_timestamp(self.subs, '00:00:-10,000'))
#
#         # Date Time
#         self.assertEqual(get_timestamp(self.subs, t('00:00:11,000')), self.subs[0].start)
#
#     def test_captions_containing_timestamp(self):
#         self.assertEqual(captions_containing_timestamp(self.subs, t('00:00:00,000')), [])
#         self.assertEqual(captions_containing_timestamp(self.subs, t('00:00:11,000')), [self.subs[0]])
#         self.assertEqual(captions_containing_timestamp(self.subs, t('00:00:12,000')), [self.subs[0]])
#         self.assertEqual(captions_containing_timestamp(self.subs, t('00:00:12,701')), [self.subs[1]])
#         self.assertEqual(captions_containing_timestamp(self.subs, t('00:00:35,000')), [])
#         self.assertEqual(captions_containing_timestamp(self.subs, t('00:00:16,708')), [self.subs[2], self.subs[3]])
#         self.assertEqual(captions_containing_timestamp(self.subs, t('00:00:17,272')), [self.subs[2], self.subs[4]])
#
#         # distanced overlaps
#         rsubs = create_blocks(1)
#         self.assertEqual(captions_containing_timestamp(rsubs, t('00:00:4,000')), [rsubs[0], rsubs[1], rsubs[2], rsubs[3]])
#         self.assertEqual(captions_containing_timestamp(rsubs, t('00:00:9,000')), [rsubs[0], rsubs[5]])
#         self.assertEqual(captions_containing_timestamp(rsubs, t('00:00:9,500')), [rsubs[0],rsubs[5]])
#         self.assertEqual(captions_containing_timestamp(rsubs, t('00:00:3,450')), [rsubs[0], rsubs[1], rsubs[2]])
#         self.assertEqual(captions_containing_timestamp(rsubs, t('00:00:5,500')), [rsubs[0], rsubs[1]])
#         self.assertEqual(captions_containing_timestamp(rsubs, t('00:00:11,000')), [])
#
#     def test_remove_caption_index(self):
#         a = sort([self.subs[0], self.subs[2], self.subs[3], self.subs[4]])
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, 1, 2)
#         self.assertEqual(list(result), a)
#
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, 1, -3)
#         self.assertEqual(list(result), a)
#
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, 1, 3)
#         self.assertEqual(list(result), sort([self.subs[0], self.subs[3], self.subs[4]]))
#
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, 2, 5)
#         self.assertEqual(list(result), sort([self.subs[0], self.subs[1]]))
#
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, -2, 3)
#         self.assertEqual(list(result), [])
#
#         rsubs = create_blocks()
#         with self.assertRaises(IndexError):
#             result = remove_caption_index(rsubs, 1, 8)
#             result = remove_caption_index(rsubs, -7, 4)
#             result = remove_caption_index(rsubs, 5, 4)
#
#         result = remove_caption_index(rsubs, 3, 1) # reverse
#         self.assertEqual(list(result), sort([self.subs[1],self.subs[2]]))
#
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, 2, 0) # reverse
#         self.assertEqual(list(result), sort([self.subs[0], self.subs[1]]))
#
#         a = sort([self.subs[2], self.subs[3]])
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, -1, -3) # reverse
#         self.assertEqual(list(result), a)
#
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, 4, 2) # reverse
#         self.assertEqual(list(result), a)
#
#         # single parameter
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, 0)
#         self.assertEqual(list(result), [])
#
#         rsubs = create_blocks()
#         result = remove_caption_index(rsubs, 2)
#         self.assertEqual(list(result), sort([self.subs[0], self.subs[1]]))
#
#     def test_remove_caption_timestamp(self):
#         result = remove_caption_timestamp([], t('00:00:00,000'), t('00:00:30,000'))
#         self.assertEqual(list(result), [])
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, rsubs[0].start, rsubs[0].end)
#         self.assertEqual(list(result), sort([self.subs[1], self.subs[2], self.subs[3], self.subs[4]]))
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, rsubs[0].start, t('00:00:14,500'))
#         self.assertEqual(list(result), sort([self.subs[2], self.subs[3], self.subs[4]]))
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, t('00:00:11,000'), t('00:00:19,738'))
#         self.assertEqual(list(result), [])
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, t('00:00:00,000'), t('00:00:30,000'))
#         self.assertEqual(list(result), [])
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, t('00:00:00,000'), t('00:00:17,500'))
#         a = [srt.Subtitle(1, t('00:00:17,500'), t('00:00:18,440'), "E"), srt.Subtitle(2, t('00:00:17,500'), t('00:00:19,738'), "C")]
#         self.assertEqual(list(result), a) # split
#
#         # reverse timestamps
#         result = remove_caption_timestamp([], t('00:00:30,000'), t('00:00:00,000'))
#         self.assertEqual(list(result), [])
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, t('00:00:30,000'), t('00:00:00,000'))
#         self.assertEqual(list(result), list(self.subs))
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, t('00:00:14,500'), rsubs[0].start)
#         self.assertEqual(list(result), sort([self.subs[0],self.subs[1]]))
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, t('00:00:19,738'), t('00:00:11,000'))
#         self.assertEqual(list(result), list(self.subs))
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, rsubs[0].end, rsubs[0].start)
#         self.assertEqual(list(result), [self.subs[0]])
#
#         rsubs = create_blocks()
#         result = remove_caption_timestamp(rsubs, rsubs[0].start, rsubs[0].start)
#         self.assertEqual(list(result), [])
