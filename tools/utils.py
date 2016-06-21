#!/usr/bin/env python

import argparse
import sys
import logging
import itertools


def basic_parser(multi_input=False):
    parser = argparse.ArgumentParser(description=__doc__)

    if multi_input:
        parser.add_argument(
            '--input', '-i', metavar='FILE',
            action='append', type=argparse.FileType('r'),
            help='the files to process',
            required=True,
        )
    else:
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
        '--no-strict',
        action='store_false', dest='strict',
        help='allow blank lines in output, your media player may explode',
    )
    parser.add_argument(
        '--debug',
        action='store_const', dest='log_level',
        const=logging.DEBUG, default=logging.WARNING,
        help='enable debug logging',
    )
    return parser


def sliding_window(seq, width=2):
    seq_iter = iter(seq)
    sliced = tuple(itertools.islice(seq_iter, width))

    if len(sliced) == width:
        yield sliced

    for elem in seq_iter:
        sliced = sliced[1:] + (elem,)
        yield sliced
