#!/usr/bin/env python

import argparse
import sys
import datetime
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
        '--ms', metavar='MILLISECONDS',
        default=datetime.timedelta(milliseconds=500),
        type=lambda ms: datetime.timedelta(milliseconds=int(ms)),
        help='if two subs being muxed are within this number of milliseconds '
             'of each other, they will get merged (default: 250)',
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
    last_sub = None
    for sub in sorted_subs:
        if last_sub is not None:
            if last_sub.start + args.ms > sub.start:
                sub.start = last_sub.start
            if last_sub.end + args.ms > sub.end:
                sub.end = last_sub.end
        last_sub = sub

    output = srt.compose(sorted_subs)
    args.output.write(output)


if __name__ == '__main__':
    main()
