#!/usr/bin/env python

import utils
import srt


def reindex(subtitles):
    for new_index, subtitle in enumerate(sorted(subtitles), start=1):
        subtitle.index = new_index
        yield subtitle


def main():
    args = utils.basic_parser().parse_args()
    subtitles_in = srt.parse(args.input.read())
    reindexed_subtitles = reindex(subtitles_in)
    output = srt.compose(reindexed_subtitles)
    args.output.write(output)


if __name__ == '__main__':
    main()
