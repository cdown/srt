from __future__ import unicode_literals

from datetime import timedelta
import sys
import unittest

import srt


def make_subtitle(start=1, end=2, index=1):
    return srt.Subtitle(
        index=index,
        start=timedelta(seconds=start),
        end=timedelta(seconds=end),
        content="x",
    )


class TestSubtitleComparison(unittest.TestCase):
    def test_foreign_reflected_comparison(self):
        class Wrapper(object):
            def __init__(self):
                self.operand = None

            def __gt__(self, other):
                self.operand = other
                return True

        sub = make_subtitle()
        wrapper = Wrapper()

        self.assertIs(sub < wrapper, True)
        self.assertIs(wrapper.operand, sub)
        self.assertIs(sub.__lt__(wrapper), NotImplemented)

    @unittest.skipIf(
        sys.version_info[0] < 3,
        "Python 2 permits ordering of unrelated objects",
    )
    def test_unsupported_operand(self):
        sub = make_subtitle()
        foreign = object()

        with self.assertRaises(TypeError):
            sub < foreign
        self.assertIs(sub.__lt__(foreign), NotImplemented)

    def test_subtitle_ordering_regression(self):
        class Child(srt.Subtitle):
            pass

        first = make_subtitle()
        second = Child(
            index=2,
            start=timedelta(seconds=1),
            end=timedelta(seconds=2),
            content="x",
        )
        third = make_subtitle(end=3)
        fourth = make_subtitle(start=2, end=3)
        items = [first, second, third, fourth]

        ordered = sorted(reversed(items))
        self.assertIs(ordered[0], first)
        self.assertIs(ordered[1], second)
        self.assertIs(ordered[2], third)
        self.assertIs(ordered[3], fourth)
        self.assertTrue(first < second)
        self.assertTrue(second > first)
        self.assertTrue(first <= first)
        self.assertTrue(first >= first)
        self.assertIs(first.__lt__(first), False)


if __name__ == "__main__":
    unittest.main()
