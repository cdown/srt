# coding=utf8

from __future__ import unicode_literals

from datetime import timedelta

import pytest

import srt


@pytest.mark.parametrize(
    "content, expected",
    [
        ("", ""),
        ("\n", ""),
        ("caption", "caption"),
        ("caption\n", "caption"),
        ("caption\n\n", "caption"),
        ("\ncaption", "caption"),
        ("one\ntwo", "one\ntwo"),
        ("one\ntwo\n", "one\ntwo"),
        (" one \n", " one "),
        ("字幕\n", "字幕"),
        ("one\n\n two\n", "one\n two"),
        (" \n", " "),
    ],
)
def test_make_legal_content_removes_boundary_newlines(content, expected):
    assert srt.make_legal_content(content) == expected


@pytest.mark.parametrize("content", ["caption", "one\ntwo"])
@pytest.mark.parametrize("eol", ["\n", "\r\n"])
@pytest.mark.parametrize("strict", [False, True])
def test_subtitle_trailing_newline_output(content, eol, strict):
    subtitle = srt.Subtitle(
        1, timedelta(seconds=1), timedelta(seconds=2), content + "\n"
    )
    expected_content = content if strict else content + "\n"
    expected = "1\n00:00:01,000 --> 00:00:02,000\n" + expected_content + "\n\n"

    assert subtitle.to_srt(strict=strict, eol=eol) == expected.replace("\n", eol)


@pytest.mark.parametrize("eol", ["\n", "\r\n"])
def test_compose_does_not_add_extra_blank_lines(eol):
    subtitles = [
        srt.Subtitle(1, timedelta(seconds=1), timedelta(seconds=2), "first\n"),
        srt.Subtitle(2, timedelta(seconds=3), timedelta(seconds=4), "second\n"),
    ]
    expected = (
        "1\n00:00:01,000 --> 00:00:02,000\nfirst\n\n"
        "2\n00:00:03,000 --> 00:00:04,000\nsecond\n\n"
    )

    assert srt.compose(subtitles, eol=eol) == expected.replace("\n", eol)
