#!/usr/bin/env python

import argparse
import sys
import logging


def basic_parser():
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
    parser.add_argument(
        '--debug',
        action="store_const", dest='log_level',
        const=logging.DEBUG, default=logging.WARNING,
        help='enable debug logging',
    )
    return parser
