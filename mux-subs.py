#!/usr/bin/env python

import argparse
import sys
import srt
import logging


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--input', '-i', metavar='FILE',
        action='append', type=argparse.FileType('r'),
        help='the files to process (default: stdin)',
        required=True,
    )
    parser.add_argument(
        '--output', '-o', metavar='FILE',
        default=sys.stdout,
        type=argparse.FileType('w'),
        help='the file to write to (default: stdout)',
    )
    parser.add_argument(
        '--debug',
        action="store_const", dest='log_level',
        const=logging.DEBUG, default=logging.WARNING,
        help='enable debug logging',
    )
    return parser.parse_args()


def main():
    args = parse_args()

    unordered_muxed_subs = []
    for file_input in args.input:
        unordered_muxed_subs.extend(srt.parse(file_input.read()))

    muxed_subs = srt.sort_and_reindex(unordered_muxed_subs)
    output = srt.compose(muxed_subs)
    args.output.write(output)


if __name__ == '__main__':
    main()
