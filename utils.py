#!/usr/bin/env python

import argparse
import sys


def parse_args():
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
