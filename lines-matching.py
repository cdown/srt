#!/usr/bin/env python

import importlib
import srt
import utils


def strip_to_matching_lines_only(subtitles, imports, func_str):
    for import_name in imports:
        real_import = importlib.import_module(import_name)
        globals()[import_name] = real_import

    func = eval(func_str)

    for subtitle in subtitles:
        subtitle_lines = subtitle.content.splitlines()
        matching_subtitle_lines = (
            line for line in subtitle_lines
            if func(line)
        )
        subtitle.content = '\n'.join(matching_subtitle_lines)
        yield subtitle


def parse_args():
    parser = utils.basic_parser()
    parser.add_argument(
        '-f', '--func',
        help='a function to use to match lines',
        required=True,
    )
    parser.add_argument(
        '-m', '--module',
        help='modules to import in the function context',
        action='append', default=[],
    )
    return parser.parse_args()


def main():
    args = parse_args()
    subtitles_in = srt.parse(args.input.read())
    matching_subtitles_only = strip_to_matching_lines_only(
        subtitles_in, args.module, args.func,
    )
    output = srt.compose(matching_subtitles_only, strict=args.strict)
    args.output.write(output)


if __name__ == '__main__':
    main()
