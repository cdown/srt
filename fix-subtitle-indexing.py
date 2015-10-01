#!/usr/bin/env python

import utils
import srt


def main():
    args = utils.basic_parser().parse_args()
    subtitles_in = srt.parse(args.input.read())
    output = srt.compose(subtitles_in, strict=args.strict)
    args.output.write(output)


if __name__ == '__main__':
    main()
