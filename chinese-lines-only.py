#!/usr/bin/env python

from hanzidentifier import has_chinese
from utils import run


def strip_to_chinese_lines_only(subtitles):
    for subtitle in subtitles:
        subtitle_lines = subtitle.content.splitlines()
        chinese_subtitle_lines = (
            line for line in subtitle_lines
            if has_chinese(line)
        )
        subtitle.content = '\n'.join(chinese_subtitle_lines)
        yield subtitle


if __name__ == '__main__':
    run(strip_to_chinese_lines_only)
