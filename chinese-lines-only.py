#!/usr/bin/env python

from hanzidentifier import has_chinese
import srt
import utils


def strip_to_chinese_lines_only(subtitles):
    for subtitle in subtitles:
        subtitle_lines = subtitle.content.splitlines()
        chinese_subtitle_lines = (
            line for line in subtitle_lines
            if has_chinese(line)
        )
        subtitle.content = '\n'.join(chinese_subtitle_lines)
        yield subtitle


def main():
    args = utils.basic_parser().parse_args()
    subtitles_in = srt.parse_file(args.input)
    chinese_subtitles_only = strip_to_chinese_lines_only(subtitles_in)
    srt.compose_file(chinese_subtitles_only, args.output)


if __name__ == '__main__':
    main()
