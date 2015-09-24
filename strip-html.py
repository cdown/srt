#!/usr/bin/env python

import re
import srt
import utils


def strip_html_from_subs(subtitles):
    for subtitle in subtitles:
        subtitle_lines = subtitle.content.splitlines()
        stripped_subtitle_lines = (
            re.sub('<[^<]+?>', '', line) for line in subtitle_lines
        )
        subtitle.content = '\n'.join(stripped_subtitle_lines)
        yield subtitle


def main():
    args = utils.basic_parser().parse_args()
    subtitles_in = srt.parse_file(args.input)
    stripped_subs = strip_html_from_subs(subtitles_in)
    srt.compose_file(stripped_subs, args.output)


if __name__ == '__main__':
    main()
