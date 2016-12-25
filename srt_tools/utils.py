#!/usr/bin/env python

import argparse
import srt
import sys
import logging
import itertools
import collections


DEFAULT_ENCODING = 'utf8'

log = logging.getLogger(__name__)


def basic_parser(multi_input=False):
    parser = argparse.ArgumentParser(description=__doc__)

    # Cannot use argparse.FileType as we need to know the encoding from the
    # args

    if multi_input:
        parser.add_argument(
            '--input', '-i', metavar='FILE',
            action='append',
            help='the files to process',
            required=True,
        )
    else:
        parser.add_argument(
            '--input', '-i', metavar='FILE',
            default=sys.stdin,
            help='the file to process (default: stdin)',
        )

    parser.add_argument(
        '--output', '-o', metavar='FILE',
        default=sys.stdout,
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

    # Can't set default= here because we need to know whether this was
    # explicitly specified for -e warnings
    parser.add_argument(
        '--encoding', '-e',
        help='the encoding to read/write files in (default: utf8)'
    )
    return parser


def set_basic_args(args):
    encoding_explicitly_specified = True
    if args.encoding is None:
        args.encoding = DEFAULT_ENCODING
        encoding_explicitly_specified = False

    for stream_name in ('input', 'output'):
        stream = getattr(args, stream_name)
        if stream in (sys.stdin, sys.stdout):
            if stream is args.input:
                args.input = srt.parse(args.input.read())
            if encoding_explicitly_specified:
                log.warning(
                    '-e/--encoding has no effect on %s, you need to use '
                    '--input or --output', stream.name,
                )
        else:
            if stream is args.input:
                if isinstance(args.input, collections.MutableSequence):
                    for i, input_fn in enumerate(args.input):
                        with open(input_fn, encoding=args.encoding) as input_f:
                            args.input[i] = srt.parse(input_f.read())
                else:
                    with open(stream, encoding=args.encoding) as input_f:
                        args.input = srt.parse(input_f.read())
            else:
                args.output = open(args.output, 'w+', encoding=args.encoding)


def sliding_window(seq, width=2):
    seq_iter = iter(seq)
    sliced = tuple(itertools.islice(seq_iter, width))

    if len(sliced) == width:
        yield sliced

    for elem in seq_iter:
        sliced = sliced[1:] + (elem,)
        yield sliced
