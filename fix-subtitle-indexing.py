#!/usr/bin/env python

import utils
import srt


def reindex(subtitles):
    for new_index, subtitle in enumerate(sorted(subtitles), start=1):
        subtitle.index = new_index
        yield subtitle


def main():
    args = utils.parse_args()
    subtitles_in = srt.parse_file(args.input)
    reindexed_subtitles = reindex(subtitles_in)
    srt.compose_file(reindexed_subtitles, args.output)


if __name__ == '__main__':
    main()
