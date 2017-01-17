#!/usr/bin/env python

import argparse
import srt
import logging
import sys
import itertools
import collections

if sys.version_info < (3,):
    from codecs import open as _open
else:
    _open = open

DASH_STREAM_MAP = {
    'input': sys.stdin,
    'output': sys.stdout,
}

DEFAULT_ENCODING = 'utf8'

log = logging.getLogger(__name__)

STREAM_ENC_MSG = (
    '-e/--encoding has no effect on %s, you need to use --input or --output '
    'with a real file'
)


def dash_to_stream(arg, arg_type):
    if arg == '-':
        return DASH_STREAM_MAP[arg_type]
    return arg


def basic_parser(multi_input=False, no_output=False):
    parser = argparse.ArgumentParser(description=__doc__)

    # Cannot use argparse.FileType as we need to know the encoding from the
    # args

    if multi_input:
        parser.add_argument(
            '--input', '-i', metavar='FILE',
            action='append',
            type=lambda arg: dash_to_stream(arg, 'input'),
            help='the files to process',
            required=True,
        )
    else:
        parser.add_argument(
            '--input', '-i', metavar='FILE',
            default=sys.stdin,
            type=lambda arg: dash_to_stream(arg, 'input'),
            help='the file to process (default: stdin)',
        )

    if not no_output:
        parser.add_argument(
            '--output', '-o', metavar='FILE',
            default=sys.stdout,
            type=lambda arg: dash_to_stream(arg, 'output'),
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

    # TODO: dedupe some of this
    for stream_name in ('input', 'output'):
        log.debug('Processing stream "%s"', stream_name)

        try:
            stream = getattr(args, stream_name)
        except AttributeError:
            # For example, in the case of no_output
            continue

        log.debug('Got %r as stream', stream)
        if stream in DASH_STREAM_MAP.values():
            log.debug('%s in DASH_STREAM_MAP', stream_name)
            if stream is args.input:
                args.input = srt.parse(args.input.read())
            if encoding_explicitly_specified:
                log.warning(STREAM_ENC_MSG, stream.name)
        else:
            log.debug('%s not in DASH_STREAM_MAP', stream_name)
            if stream is args.input:
                if isinstance(args.input, collections.MutableSequence):
                    for i, input_fn in enumerate(args.input):
                        if input_fn in DASH_STREAM_MAP.values():
                            if encoding_explicitly_specified:
                                log.warning(STREAM_ENC_MSG, input_fn.name)
                            if stream is args.input:
                                args.input[i] = srt.parse(input_fn.read())
                        else:
                            with _open(input_fn, encoding=args.encoding) as f:
                                args.input[i] = srt.parse(f.read())
                else:
                    with _open(stream, encoding=args.encoding) as input_f:
                        args.input = srt.parse(input_f.read())
            else:
                args.output = _open(args.output, 'w+', encoding=args.encoding)


def compose_suggest_on_fail(subs, strict=True):
    try:
        return srt.compose(subs, strict=strict)
    except srt.SRTParseError as thrown_exc:
        log.fatal(
            'Parsing failed, maybe you need to pass a different encoding '
            'with --encoding?'
        )
        raise


def sliding_window(seq, width=2):
    seq_iter = iter(seq)
    sliced = tuple(itertools.islice(seq_iter, width))

    if len(sliced) == width:
        yield sliced

    for elem in seq_iter:
        sliced = sliced[1:] + (elem,)
        yield sliced
