#!/usr/bin/env python

import argparse
import codecs
import srt
import logging
import sys
import itertools
import collections

if sys.version_info < (3,):
    from codecs import open as _open
else:
    _open = open

STDIN_BYTESTREAM = getattr(sys.stdin, "buffer", sys.stdin)
STDOUT_BYTESTREAM = getattr(sys.stdout, "buffer", sys.stdout)

DASH_STREAM_MAP = {"input": STDIN_BYTESTREAM, "output": STDOUT_BYTESTREAM}

log = logging.getLogger(__name__)


def noop(stream):
    """
    Used when we didn't explicitly specify a stream to avoid using
    codecs.get{reader,writer}
    """
    return stream


def dash_to_stream(arg, arg_type):
    if arg == "-":
        return DASH_STREAM_MAP[arg_type]
    return arg


def basic_parser(multi_input=False, no_output=False):
    parser = argparse.ArgumentParser(description=__doc__)

    # Cannot use argparse.FileType as we need to know the encoding from the
    # args

    if multi_input:
        parser.add_argument(
            "--input",
            "-i",
            metavar="FILE",
            action="append",
            type=lambda arg: dash_to_stream(arg, "input"),
            help="the files to process",
            required=True,
        )
    else:
        parser.add_argument(
            "--input",
            "-i",
            metavar="FILE",
            default=STDIN_BYTESTREAM,
            type=lambda arg: dash_to_stream(arg, "input"),
            help="the file to process (default: stdin)",
        )

    if not no_output:
        parser.add_argument(
            "--output",
            "-o",
            metavar="FILE",
            default=STDOUT_BYTESTREAM,
            type=lambda arg: dash_to_stream(arg, "output"),
            help="the file to write to (default: stdout)",
        )

    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="allow blank lines in output, your media player may explode",
    )
    parser.add_argument(
        "--debug",
        action="store_const",
        dest="log_level",
        const=logging.DEBUG,
        default=logging.INFO,
        help="enable debug logging",
    )

    parser.add_argument(
        "--encoding", "-e", help="the encoding to read/write files in (default: utf8)"
    )
    return parser


def set_basic_args(args):
    # TODO: dedupe some of this
    for stream_name in ("input", "output"):
        log.debug('Processing stream "%s"', stream_name)

        try:
            stream = getattr(args, stream_name)
        except AttributeError:
            # For example, in the case of no_output
            continue

        # We don't use system default encoding, because usually one runs this
        # on files they got from elsewhere. As such, be opinionated that these
        # files are probably UTF-8. Looking for the BOM on reading allows us to
        # be more liberal with what we accept, without adding BOMs on write.
        read_encoding = args.encoding or "utf-8-sig"
        write_encoding = args.encoding or "utf-8"

        r_enc = codecs.getreader(read_encoding)
        w_enc = codecs.getwriter(write_encoding)

        log.debug("Got %r as stream", stream)
        if stream in DASH_STREAM_MAP.values():
            log.debug("%s in DASH_STREAM_MAP", stream_name)
            if stream is args.input:
                args.input = srt.parse(r_enc(args.input).read())
            elif stream is args.output:
                args.output = w_enc(args.output)
        else:
            log.debug("%s not in DASH_STREAM_MAP", stream_name)
            if stream is args.input:
                if isinstance(args.input, collections.MutableSequence):
                    for i, input_fn in enumerate(args.input):
                        if input_fn in DASH_STREAM_MAP.values():
                            if stream is args.input:
                                args.input[i] = srt.parse(r_enc(input_fn).read())
                        else:
                            f = _open(input_fn, "r", encoding=read_encoding)
                            with f:
                                args.input[i] = srt.parse(f.read())
                else:
                    f = _open(stream, "r", encoding=read_encoding)
                    with f:
                        args.input = srt.parse(f.read())
            else:
                args.output = _open(args.output, "w", encoding=write_encoding)


def compose_suggest_on_fail(subs, strict=True):
    try:
        return srt.compose(subs, strict=strict)
    except srt.SRTParseError as thrown_exc:
        log.fatal(
            "Parsing failed, maybe you need to pass a different encoding "
            "with --encoding?"
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
