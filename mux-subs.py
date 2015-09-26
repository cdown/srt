#!/usr/bin/env python

import argparse
import sys
import datetime
import srt
import logging
import utils


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
        '--ms', metavar='MILLISECONDS',
        default=datetime.timedelta(milliseconds=350),
        type=lambda ms: datetime.timedelta(milliseconds=int(ms)),
        help='if subs being muxed are within this number of milliseconds '
             'of each other, they will get merged (default: 350)',
    )
    parser.add_argument(
        '--width',
        default=5, type=int,
        help='the number of subs to consider merging (default: %(default)s)',
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

    sorted_subs = sorted(unordered_muxed_subs)

    # Merge subs with similar start/end times together. This prevents the
    # subtitles jumping around the screen.
    for subs in utils.sliding_window(sorted_subs, width=args.width):
        current_sub = subs[0]
        future_subs = subs[1:]

        for future_sub in future_subs:
            if current_sub.start + args.ms > future_sub.start:
                future_sub.start = current_sub.start
            if current_sub.end + args.ms > future_sub.end:
                future_sub.end = current_sub.end

    output = srt.compose(sorted_subs)
    args.output.write(output)


if __name__ == '__main__':
    main()
