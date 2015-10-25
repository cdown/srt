#!/usr/bin/env python

import srt
import datetime
import utils


def timedelta_to_milliseconds(delta):
    return delta.days * 86400000 + \
           delta.seconds * 1000 + \
           delta.microseconds / 1000

def parse_args():
    def srt_timestamp_to_milliseconds(parser, arg):
        try:
            delta = srt.srt_timestamp_to_timedelta(arg)
        except ValueError:
            parser.error('not a valid SRT timestamp: %s' % arg)
        else:
            return timedelta_to_milliseconds(delta)

    parser = utils.basic_parser()
    parser.add_argument(
        '--desynced-start',
        type=lambda arg: srt_timestamp_to_milliseconds(parser, arg),
        required=True,
        help='the first desynchronised timestamp',
    )
    parser.add_argument(
        '--synced-start',
        type=lambda arg: srt_timestamp_to_milliseconds(parser, arg),
        required=True,
        help='the first synchronised timestamp',
    )
    parser.add_argument(
        '--desynced-end',
        type=lambda arg: srt_timestamp_to_milliseconds(parser, arg),
        required=True,
        help='the second desynchronised timestamp',
    )
    parser.add_argument(
        '--synced-end',
        type=lambda arg: srt_timestamp_to_milliseconds(parser, arg),
        required=True,
        help='the second synchronised timestamp',
    )
    return parser.parse_args()


def calc_correction(synced_start, synced_end, desynced_start, desynced_end):
    angular = (synced_end - synced_start) / (desynced_end - desynced_start)
    linear = synced_end - angular * desynced_end
    return angular, linear


def correct_time(current_msecs, angular, linear):
    return round(current_msecs * angular + linear)


def correct_timedelta(bad_delta, angular, linear):
    bad_msecs = timedelta_to_milliseconds(bad_delta)
    good_msecs = correct_time(bad_msecs, angular, linear)
    good_delta = datetime.timedelta(milliseconds=good_msecs)
    return good_delta


def linear_correct_subs(subtitles, angular, linear):
    for subtitle in subtitles:
        subtitle.start = correct_timedelta(subtitle.start, angular, linear)
        subtitle.end = correct_timedelta(subtitle.end, angular, linear)
        yield subtitle


def main():
    args = parse_args()
    angular, linear = calc_correction(
        args.synced_start, args.synced_end,
        args.desynced_start, args.desynced_end,
    )
    subtitles_in = srt.parse(args.input.read())
    corrected_subs = linear_correct_subs(subtitles_in, angular, linear)
    output = srt.compose(corrected_subs, strict=args.strict)
    args.output.write(output)


if __name__ == '__main__':
    main()
