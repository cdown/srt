#!/usr/bin/env python

import argparse
import srt
import sys


def parse_basic_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--input', '-i', metavar='FILE',
        default=sys.stdin, type=argparse.FileType('r'),
        help='the file to process (default: stdin)',
    )
    parser.add_argument(
        '--output', '-o', metavar='FILE',
        default=sys.stdout,
        type=argparse.FileType('w'),
        help='the file to write to (default: stdout)',
    )
    return parser.parse_args()


def run(func):
    args = parse_basic_args()
    subtitles_in = srt.parse_file(args.input)
    subtitles_out = func(subtitles_in)
    srt.compose_file(subtitles_out, args.output)
