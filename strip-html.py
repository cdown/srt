#!/usr/bin/env python

import re
import srt
import utils
import logging


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
    logging.basicConfig(level=args.log_level)
    subtitles_in = srt.parse(args.input.read())
    stripped_subs = strip_html_from_subs(subtitles_in)
    output = srt.compose(stripped_subs)
    args.output.write(output)


if __name__ == '__main__':
    main()
