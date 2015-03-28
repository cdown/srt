#!/usr/bin/env python

import srt
import utils


def reindex(subtitles):
    for new_index, subtitle in enumerate(sorted(subtitles), start=1):
        subtitle.index = new_index
        yield subtitle


def main():
    args = utils.parse_basic_args()
    subtitles_with_bad_indexes = srt.parse_file(args.input)
    subtitles_with_good_indexes = reindex(subtitles_with_bad_indexes)
    srt.compose_file(subtitles_with_good_indexes, args.output)


if __name__ == '__main__':
    main()
