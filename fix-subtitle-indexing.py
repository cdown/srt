#!/usr/bin/env python

from utils import run


def reindex(subtitles):
    for new_index, subtitle in enumerate(sorted(subtitles), start=1):
        subtitle.index = new_index
        yield subtitle


if __name__ == '__main__':
    run(reindex)
