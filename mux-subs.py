#!/usr/bin/env python

import argparse
import sys
import datetime
import srt
import utils
import logging
import operator

log = logging.getLogger(__name__)

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


def merge_subs(subs, acceptable_diff, attr, width):
    '''
    Merge subs with similar start/end times together. This prevents the
    subtitles jumping around the screen.

    The merge is done in-place.
    '''
    sorted_subs = sorted(subs, key=operator.attrgetter(attr))

    for subs in utils.sliding_window(sorted_subs, width=width):
        current_sub = subs[0]
        future_subs = subs[1:]
        current_comp = getattr(current_sub, attr)

        for future_sub in future_subs:
            future_comp = getattr(future_sub, attr)
            if current_comp + acceptable_diff > future_comp:
                log.debug(
                    "Merging %d's %s time into %d",
                    future_sub.index, attr, current_sub.index,
                )
                setattr(future_sub, attr, current_comp)


def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level)

    muxed_subs = []
    for file_input in args.input:
        muxed_subs.extend(srt.parse(file_input.read()))

    merge_subs(muxed_subs, args.ms, 'start', args.width)
    merge_subs(muxed_subs, args.ms, 'end', args.width)

    output = srt.compose(muxed_subs)
    args.output.write(output)


if __name__ == '__main__':
    main()
