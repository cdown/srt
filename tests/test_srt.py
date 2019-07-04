#!/usr/bin/env python
# coding=utf8

from __future__ import unicode_literals
from datetime import timedelta
import functools
import string
from io import StringIO

from hypothesis import given, settings, HealthCheck
import hypothesis.strategies as st
from nose.tools import (
    eq_ as eq,
    assert_not_equal as neq,
    assert_raises,
    assert_false,
    assert_true,
    assert_in,
)

import srt

try:
    from nose.tools import assert_count_equal
except ImportError:  # Python 2 fallback
    from nose.tools import assert_items_equal as assert_count_equal

settings.register_profile(
    "base", settings(suppress_health_check=[HealthCheck.too_slow])
)
settings.load_profile("base")

HOURS_IN_DAY = 24
TIMEDELTA_MAX_DAYS = 999999999
CONTENTLESS_SUB = functools.partial(
    srt.Subtitle, index=1, start=timedelta(seconds=1), end=timedelta(seconds=2)
)


def is_strictly_legal_content(content):
    """
    Filter out things that would violate strict mode. Illegal content
    includes:

    - A content section that starts or ends with a newline
    - A content section that contains blank lines
    """

    if content.strip("\r\n") != content:
        return False
    elif not content.strip():
        return False
    elif "\n\n" in content:
        return False
    else:
        return True


def subs_eq(got, expected, any_order=False):
    """
    Compare Subtitle objects using vars() so that differences are easy to
    identify.
    """
    got_vars = [vars(sub) for sub in got]
    expected_vars = [vars(sub) for sub in expected]
    if any_order:
        assert_count_equal(got_vars, expected_vars)
    else:
        eq(got_vars, expected_vars)


def timedeltas(min_value=0, max_value=TIMEDELTA_MAX_DAYS):
    """
    A Hypothesis strategy to generate timedeltas.

    Right now {min,max}_value are shoved into multiple fields in timedelta(),
    which is not very customisable, but it's good enough for our current test
    purposes. If you need more precise control, you may need to add more
    parameters to this function to be able to customise more freely.
    """
    time_unit_strategy = st.integers(min_value=min_value, max_value=max_value)
    timestamp_strategy = st.builds(
        timedelta,
        hours=time_unit_strategy,
        minutes=time_unit_strategy,
        seconds=time_unit_strategy,
    )
    return timestamp_strategy


def subtitles(strict=True):
    """A Hypothesis strategy to generate Subtitle objects."""
    # max_value settings are just to avoid overflowing TIMEDELTA_MAX_DAYS by
    # using arbitrary low enough numbers.
    #
    # We also skip subs with start time >= end time, so we split them into two
    # groups to avoid overlap.
    start_timestamp_strategy = timedeltas(min_value=0, max_value=500000)
    end_timestamp_strategy = timedeltas(min_value=500001, max_value=999999)

    # If we want to test \r, we'll test it by ourselves. It makes testing
    # harder without because we don't get the same outputs as inputs on Unix.
    content_strategy = st.text(min_size=1).filter(lambda x: "\r" not in x)
    proprietary_strategy = st.text().filter(
        lambda x: all(eol not in x for eol in "\r\n")
    )

    if strict:
        content_strategy = content_strategy.filter(is_strictly_legal_content)

    subtitle_strategy = st.builds(
        srt.Subtitle,
        index=st.integers(min_value=0),
        start=start_timestamp_strategy,
        end=end_timestamp_strategy,
        proprietary=proprietary_strategy,
        content=content_strategy,
    )

    return subtitle_strategy


@given(st.lists(subtitles()))
def test_compose_and_parse_from_file(input_subs):
    srt_file = StringIO(srt.compose(input_subs, reindex=False))
    reparsed_subs = srt.parse(srt_file)
    subs_eq(reparsed_subs, input_subs)


@given(st.lists(subtitles()))
def test_compose_and_parse_strict(input_subs):
    composed = srt.compose(input_subs, reindex=False)
    reparsed_subs = srt.parse(composed)
    subs_eq(reparsed_subs, input_subs)


@given(st.lists(subtitles()))
def test_can_compose_without_ending_blank_line(input_subs):
    """
    Many sub editors don't add a blank line to the end, and many editors accept
    it. We should just accept this too in input.
    """
    composed = srt.compose(input_subs, reindex=False)
    composed_without_ending_blank = composed[:-1]
    reparsed_subs = srt.parse(composed_without_ending_blank)
    subs_eq(reparsed_subs, input_subs)


@given(st.lists(subtitles()))
def test_can_compose_without_eol_at_all(input_subs):
    composed = srt.compose(input_subs, reindex=False)
    composed_without_ending_blank = composed.rstrip("\r\n")
    reparsed_subs = srt.parse(composed_without_ending_blank)
    subs_eq(reparsed_subs, input_subs)


@given(st.text().filter(is_strictly_legal_content))
def test_compose_and_parse_strict_mode(content):
    content = "\n" + content + "\n\n" + content + "\n"
    sub = CONTENTLESS_SUB(content=content)

    parsed_strict = list(srt.parse(sub.to_srt()))[0]
    parsed_unstrict = list(srt.parse(sub.to_srt(strict=False)))[0]

    # Strict mode should remove blank lines in content, leading, and trailing
    # newlines.
    assert_false(parsed_strict.content.startswith("\n"))
    assert_false(parsed_strict.content.endswith("\n"))
    assert_false("\n\n" in parsed_strict.content)

    # When strict mode is false, no processing should be applied to the
    # content (other than \r\n becoming \n).
    eq(parsed_unstrict.content, sub.content.replace("\r\n", "\n"))


@given(st.integers(min_value=1, max_value=TIMEDELTA_MAX_DAYS))
def test_timedelta_to_srt_timestamp_can_go_over_24_hours(days):
    srt_timestamp = srt.timedelta_to_srt_timestamp(timedelta(days=days))
    srt_timestamp_hours = int(srt_timestamp.split(":")[0])
    eq(srt_timestamp_hours, days * HOURS_IN_DAY)


@given(subtitles())
def test_subtitle_equality(sub_1):
    sub_2 = srt.Subtitle(**vars(sub_1))
    eq(sub_1, sub_2)


@given(subtitles())
def test_subtitle_inequality(sub_1):
    sub_2 = srt.Subtitle(**vars(sub_1))
    sub_2.index += 1
    neq(sub_1, sub_2)


@given(subtitles())
def test_subtitle_from_scratch_equality(subtitle):
    srt_block = subtitle.to_srt()

    # Get two totally new sets of objects so as not to affect the hash
    # comparison
    sub_1 = list(srt.parse(srt_block))[0]
    sub_2 = list(srt.parse(srt_block))[0]

    subs_eq([sub_1], [sub_2])
    # In case subs_eq and eq disagree for some reason
    eq(sub_1, sub_2)
    eq(hash(sub_1), hash(sub_2))


@given(st.lists(subtitles()))
def test_parsing_spaced_arrow(subs):
    spaced_block = srt.compose(subs, reindex=False, strict=False).replace("-->", "- >")
    reparsed_subtitles = srt.parse(spaced_block)
    subs_eq(reparsed_subtitles, subs)


@given(st.lists(subtitles()))
def test_parsing_content_with_blank_lines(subs):
    for subtitle in subs:
        # We stuff a blank line in the middle so as to trigger the "special"
        # content parsing for erroneous SRT files that have blank lines.
        subtitle.content = subtitle.content + "\n\n" + subtitle.content

    reparsed_subtitles = srt.parse(srt.compose(subs, reindex=False, strict=False))
    subs_eq(reparsed_subtitles, subs)


@given(st.lists(subtitles()))
def test_parsing_no_content(subs):
    for subtitle in subs:
        subtitle.content = ""

    reparsed_subtitles = srt.parse(srt.compose(subs, reindex=False, strict=False))
    subs_eq(reparsed_subtitles, subs)


@given(st.lists(subtitles()), st.lists(subtitles()), st.text(alphabet="\n\r\t "))
def test_subs_missing_content_removed(content_subs, contentless_subs, contentless_text):
    for sub in contentless_subs:
        sub.content = contentless_text

    subs = contentless_subs + content_subs
    composed_subs = list(srt.sort_and_reindex(subs, in_place=True))

    # We should have composed the same subs as there are in content_subs, as
    # all contentless_subs should have been stripped.
    subs_eq(composed_subs, content_subs, any_order=True)

    # The subtitles should be reindexed starting at start_index, excluding
    # contentless subs
    default_start_index = 1
    eq(
        [sub.index for sub in composed_subs],
        list(range(default_start_index, default_start_index + len(composed_subs))),
    )


@given(
    st.lists(subtitles()),
    st.lists(subtitles()),
    timedeltas(min_value=-999, max_value=-1),
)
def test_subs_starts_before_zero_removed(positive_subs, negative_subs, negative_td):
    for sub in negative_subs:
        sub.start = negative_td
        sub.end = negative_td  # Just to avoid tripping any start >= end errors

    subs = positive_subs + negative_subs
    composed_subs = list(srt.sort_and_reindex(subs, in_place=True))

    # There should be no negative subs
    subs_eq(composed_subs, positive_subs, any_order=True)


@given(st.lists(subtitles(), min_size=1), st.integers(min_value=0))
def test_sort_and_reindex(input_subs, start_index):
    for sub in input_subs:
        # Pin all subs to same end time so that start time is compared only,
        # must be guaranteed to be < sub.start, see how
        # start_timestamp_strategy is done
        sub.end = timedelta(500001)

    reindexed_subs = list(
        srt.sort_and_reindex(input_subs, start_index=start_index, in_place=True)
    )

    # The subtitles should be reindexed starting at start_index
    eq(
        [sub.index for sub in reindexed_subs],
        list(range(start_index, start_index + len(input_subs))),
    )

    # The subtitles should be sorted by start time
    expected_sorting = sorted(input_subs, key=lambda sub: sub.start)
    eq(reindexed_subs, expected_sorting)


@given(st.lists(subtitles()))
def test_sort_and_reindex_no_skip(input_subs):
    # end time > start time should not trigger a skip if skip=False
    for sub in input_subs:
        old_start = sub.start
        sub.start = sub.end
        sub.end = old_start

    reindexed_subs = list(srt.sort_and_reindex(input_subs, skip=False))

    # Nothing should have been skipped
    eq(len(reindexed_subs), len(input_subs))


@given(st.lists(subtitles(), min_size=1))
def test_sort_and_reindex_same_start_time_uses_end(input_subs):
    for sub in input_subs:
        # Pin all subs to same start time so that end time is compared only
        sub.start = timedelta(1)

    reindexed_subs = list(srt.sort_and_reindex(input_subs, in_place=True))

    # The subtitles should be sorted by end time when start time is the same
    expected_sorting = sorted(input_subs, key=lambda sub: sub.end)
    eq(reindexed_subs, expected_sorting)


@given(st.lists(subtitles(), min_size=1), st.integers(min_value=0))
def test_sort_and_reindex_not_in_place_matches(input_subs, start_index):
    # Make copies for both sort_and_reindex calls so that they can't affect
    # each other
    not_in_place_subs = [srt.Subtitle(**vars(sub)) for sub in input_subs]
    in_place_subs = [srt.Subtitle(**vars(sub)) for sub in input_subs]

    nip_ids = [id(sub) for sub in not_in_place_subs]
    ip_ids = [id(sub) for sub in in_place_subs]

    not_in_place_output = list(
        srt.sort_and_reindex(not_in_place_subs, start_index=start_index)
    )
    in_place_output = list(
        srt.sort_and_reindex(in_place_subs, start_index=start_index, in_place=True)
    )

    # The results in each case should be the same
    subs_eq(not_in_place_output, in_place_output)

    # Not in place sort_and_reindex should have created new subs
    assert_false(any(id(sub) in nip_ids for sub in not_in_place_output))

    # In place sort_and_reindex should be reusing the same subs
    assert_true(all(id(sub) in ip_ids for sub in in_place_output))


@given(
    st.lists(subtitles(), min_size=1),
    st.integers(min_value=0),
    st.text(min_size=1),
    timedeltas(),
)
def test_parser_noncontiguous(subs, fake_idx, garbage, fake_timedelta):
    composed = srt.compose(subs)

    # Put some garbage between subs that should trigger our failed parsing
    # detection. Since we do some magic to try and detect blank lines that
    # don't really delimit subtitles, it has to look at least a little like an
    # SRT block.
    srt_timestamp = srt.timedelta_to_srt_timestamp(fake_timedelta)
    composed = composed.replace(
        "\n\n", "\n\n%d\n%s %s" % (fake_idx, srt_timestamp, garbage)
    )

    with assert_raises(srt.SRTParseError):
        list(srt.parse(composed))


@given(
    st.lists(subtitles(), min_size=1),
    st.integers(min_value=0),
    st.text(min_size=1),
    timedeltas(),
)
def test_parser_didnt_match_to_end_raises(subs, fake_idx, garbage, fake_timedelta):
    srt_blocks = [sub.to_srt() for sub in subs]
    srt_timestamp = srt.timedelta_to_srt_timestamp(fake_timedelta)
    garbage = "\n\n%d\n%s %s" % (fake_idx, srt_timestamp, garbage)
    srt_blocks.append(garbage)
    composed = "".join(srt_blocks)

    with assert_raises(srt.SRTParseError) as thrown_exc:
        list(srt.parse(composed))

    # Since we will consume as many \n as needed until we meet the lookahead
    # assertion, leading newlines in `garbage` will be stripped.
    garbage_stripped = garbage.lstrip("\n")

    eq(garbage_stripped, thrown_exc.exception.unmatched_content)
    eq(len(composed) - len(garbage_stripped), thrown_exc.exception.expected_start)
    eq(len(composed), thrown_exc.exception.actual_start)


@given(st.lists(subtitles()))
def test_parser_can_parse_with_dot_msec_delimiter(subs):
    original_srt_blocks = [sub.to_srt() for sub in subs]
    dot_srt_blocks = []

    for srt_block in original_srt_blocks:
        srt_lines = srt_block.split("\n")
        # We should only do the first two, as it might also be in the
        # proprietary metadata, causing this test to fail.
        dot_timestamp = srt_lines[1].replace(",", ".", 2)
        srt_lines[1] = dot_timestamp
        dot_srt_blocks.append("\n".join(srt_lines))

    composed_with_dots = "".join(dot_srt_blocks)
    reparsed_subs = srt.parse(composed_with_dots)
    subs_eq(reparsed_subs, subs)


@given(st.lists(subtitles()))
def test_parser_can_parse_with_fullwidth_delimiter(subs):
    original_srt_blocks = [sub.to_srt() for sub in subs]
    dot_srt_blocks = []

    for srt_block in original_srt_blocks:
        srt_lines = srt_block.split("\n")
        dot_timestamp = srt_lines[1].replace(",", "，", 1).replace(":", "：", 1)
        srt_lines[1] = dot_timestamp
        dot_srt_blocks.append("\n".join(srt_lines))

    composed_with_fullwidth = "".join(dot_srt_blocks)
    reparsed_subs = srt.parse(composed_with_fullwidth)
    subs_eq(reparsed_subs, subs)


@given(subtitles())
def test_repr_doesnt_crash(sub):
    # Not much we can do here, but we should make sure __repr__ doesn't crash
    # or anything and it does at least vaguely look like what we want
    assert_in("Subtitle", repr(sub))
    assert_in(str(sub.index), repr(sub))


@given(st.lists(subtitles()))
def test_parser_accepts_no_newline_no_content(subs):
    for sub in subs:
        # Limit size so we know how many lines to remove
        sub.content = ""

    # Remove the last \n so that there is only one
    stripped_srt_blocks = "".join(sub.to_srt()[:-1] for sub in subs)

    reparsed_subs = srt.parse(stripped_srt_blocks)
    subs_eq(reparsed_subs, subs)


@given(st.lists(subtitles()))
def test_compose_and_parse_strict_crlf(input_subs):
    composed_raw = srt.compose(input_subs, reindex=False)
    composed = composed_raw.replace("\n", "\r\n")
    reparsed_subs = list(srt.parse(composed))

    for sub in reparsed_subs:
        sub.content = sub.content.replace("\r\n", "\n")

    subs_eq(reparsed_subs, input_subs)


@given(st.lists(subtitles()), st.one_of(st.just("\n"), st.just("\r\n")))
def test_compose_and_parse_strict_custom_eol(input_subs, eol):
    composed = srt.compose(input_subs, reindex=False, eol=eol)
    reparsed_subs = srt.parse(composed)
    subs_eq(reparsed_subs, input_subs)


@given(timedeltas())
def test_srt_timestamp_to_timedelta_too_short_raises(ts):
    srt_ts = srt.timedelta_to_srt_timestamp(ts)[:-1]
    with assert_raises(ValueError):
        srt.srt_timestamp_to_timedelta(srt_ts)


@given(st.lists(subtitles()), st.lists(st.sampled_from(string.whitespace)))
def test_can_parse_index_trailing_ws(input_subs, whitespace):
    out = ""

    for sub in input_subs:
        lines = sub.to_srt().split("\n")
        lines[0] = lines[0] + "".join(whitespace)
        out += "\n".join(lines)

    reparsed_subs = srt.parse(out)
    subs_eq(reparsed_subs, input_subs)


@given(st.lists(subtitles()), st.lists(st.just("0")))
def test_can_parse_index_leading_zeroes(input_subs, zeroes):
    out = ""

    for sub in input_subs:
        lines = sub.to_srt().split("\n")
        lines[0] = "".join(zeroes) + lines[0]
        out += "\n".join(lines)

    reparsed_subs = srt.parse(out)
    subs_eq(reparsed_subs, input_subs)
