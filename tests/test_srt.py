#!/usr/bin/env python
# vim: set fileencoding=utf8
# pylint: disable=attribute-defined-outside-init

from __future__ import unicode_literals
import srt
from datetime import timedelta
from nose.tools import eq_ as eq, assert_not_equal as neq, assert_raises, \
                       assert_false
from hypothesis import given, Settings
import hypothesis.strategies as st
import functools
import os

try:
    from nose.tools import assert_count_equal
except ImportError:  # Python 2 fallback
    from nose.tools import assert_items_equal as assert_count_equal


Settings.register_profile('quick', Settings(max_examples=5))
Settings.load_profile(os.environ.get('HYPOTHESIS_PROFILE', 'default'))


TIMESTAMP_ARGS = st.tuples(
    st.integers(min_value=0),  # Hour
    st.integers(min_value=0, max_value=59),  # Minute
    st.integers(min_value=0, max_value=59),  # Second
    st.integers(min_value=0, max_value=999),  # Millisecond
)

HOURS_IN_DAY = 24
TIMEDELTA_MAX_DAYS = 999999999
CONTENTLESS_SUB = functools.partial(
    srt.Subtitle, index=1,
    start=timedelta(seconds=1), end=timedelta(seconds=2),
)
CONTENT_TEXT = st.text(min_size=1)


def is_strictly_legal_content(content):
    '''
    Filter out things that would violate strict mode. Illegal content
    includes:

    - A content section that starts or ends with a newline
    - A content section that contains blank lines
    '''

    if content.strip() != content:
        return False
    elif '\n\n' in content:
        return False
    else:
        return True


def subs_eq(got, expected, any_order=False):
    '''
    Compare Subtitle objects using vars() so that differences are easy to
    identify.
    '''
    got_vars = [vars(sub) for sub in got]
    expected_vars = [vars(sub) for sub in expected]
    if any_order:
        assert_count_equal(got_vars, expected_vars)
    else:
        eq(got_vars, expected_vars)


def subtitles(strict=True):
    '''A Hypothesis strategy to generate Subtitle objects.'''
    timestamp_strategy = st.builds(
        timedelta, hours=st.integers(min_value=0),
        minutes=st.integers(min_value=0), seconds=st.integers(min_value=0),
    )

    content_strategy = st.text(min_size=1)
    proprietary_strategy = st.text().filter(lambda x: '\n' not in x)

    if strict:
        content_strategy = content_strategy.filter(is_strictly_legal_content)

    subtitle_strategy = st.builds(
        srt.Subtitle,
        index=st.integers(min_value=0),
        start=timestamp_strategy,
        end=timestamp_strategy,
        proprietary=proprietary_strategy,
        content=content_strategy,
    )

    return subtitle_strategy


@given(st.lists(subtitles()))
def test_compose_and_parse_strict(input_subs):
    composed = srt.compose(input_subs, reindex=False)
    reparsed_subs = srt.parse(composed)
    subs_eq(reparsed_subs, input_subs)


@given(st.lists(subtitles()))
def test_can_compose_without_ending_blank_line(input_subs):
    '''
    Many sub editors don't add a blank line to the end, and many editors accept
    it. We should just accept this too in input.
    '''
    composed = srt.compose(input_subs, reindex=False)
    composed_without_ending_blank = composed[:-1]
    reparsed_subs = srt.parse(composed_without_ending_blank)
    subs_eq(reparsed_subs, input_subs)


@given(st.lists(subtitles()))
def test_can_compose_without_eol_at_all(input_subs):
    composed = srt.compose(input_subs, reindex=False)
    composed_without_ending_blank = composed.rstrip('\n')
    reparsed_subs = srt.parse(composed_without_ending_blank)
    subs_eq(reparsed_subs, input_subs)


@given(st.text().filter(is_strictly_legal_content))
def test_compose_and_parse_strict_mode(content):
    content = '\n' + content + '\n\n' + content + '\n'
    sub = CONTENTLESS_SUB(content=content)

    parsed_strict = list(srt.parse(sub.to_srt()))[0]
    parsed_unstrict = list(srt.parse(sub.to_srt(strict=False)))[0]

    # Strict mode should remove blank lines in content, leading, and trailing
    # newlines.
    assert_false(parsed_strict.content.startswith('\n'))
    assert_false(parsed_strict.content.endswith('\n'))
    assert_false('\n\n' in parsed_strict.content)

    # When strict mode is false, no processing should be applied to the
    # content.
    eq(parsed_unstrict.content, sub.content)


@given(st.integers(min_value=1, max_value=TIMEDELTA_MAX_DAYS))
def test_timedelta_to_srt_timestamp_can_go_over_24_hours(days):
    srt_timestamp = srt.timedelta_to_srt_timestamp(timedelta(days=days))
    srt_timestamp_hours = int(srt_timestamp.split(':')[0])
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
def test_subtitle_objects_hashable(subtitle):
    hash(subtitle)


@given(st.lists(subtitles()))
def test_parsing_content_with_blank_lines(subs):
    for subtitle in subs:
        # We stuff a blank line in the middle so as to trigger the "special"
        # content parsing for erroneous SRT files that have blank lines.
        subtitle.content = subtitle.content + '\n\n' + subtitle.content

    reparsed_subtitles = srt.parse(srt.compose(
        subs, reindex=False, strict=False,
    ))
    subs_eq(reparsed_subtitles, subs)


@given(st.lists(subtitles()))
def test_parsing_no_content(subs):
    for subtitle in subs:
        subtitle.content = ''

    reparsed_subtitles = srt.parse(srt.compose(
        subs, reindex=False, strict=False,
    ))
    subs_eq(reparsed_subtitles, subs)


@given(
    st.lists(subtitles()), st.lists(subtitles()), st.text(alphabet='\n\r\t '),
)
def test_subs_missing_content_removed(content_subs, contentless_subs,
                                      contentless_text):
    for sub in contentless_subs:
        sub.content = contentless_text

    subs = contentless_subs + content_subs
    composed_subs = list(srt.sort_and_reindex(subs))

    # We should have composed the same subs as there are in content_subs, as
    # all contentless_subs should have been stripped.
    subs_eq(composed_subs, content_subs, any_order=True)

    # The subtitles should be reindexed starting at start_index, excluding
    # contentless subs
    default_start_index = 1
    eq(
        [sub.index for sub in composed_subs],
        list(range(
            default_start_index, default_start_index + len(composed_subs),
        ))
    )


@given(st.lists(subtitles(), min_size=1), st.integers(min_value=0))
def test_sort_and_reindex(input_subs, start_index):
    reindexed_subs = list(
        srt.sort_and_reindex(input_subs, start_index=start_index),
    )

    # The subtitles should be reindexed starting at start_index
    eq(
        [sub.index for sub in reindexed_subs],
        list(range(start_index, start_index + len(input_subs)))
    )

    # The subtitles should be sorted by start time
    expected_sorting = sorted(input_subs, key=lambda sub: sub.start)
    eq(reindexed_subs, expected_sorting)


@given(
    st.lists(subtitles(), min_size=1), st.integers(min_value=0),
    st.integers(min_value=0), st.text(min_size=1),
)
def test_parser_noncontiguous(subs, fake_idx, fake_hours, garbage):
    composed = srt.compose(subs)

    # Put some garbage between subs that should trigger our failed parsing
    # detection. Since we do some magic to try and detect blank lines that
    # don't really delimit subtitles, it has to look at least a little like an
    # SRT block.
    composed = composed.replace(
        '\n\n', '\n\n%d\n%d:%s' % (
            fake_idx, fake_hours, garbage,
        )
    )

    with assert_raises(srt.SRTParseError):
        list(srt.parse(composed))


@given(
    st.lists(subtitles(), min_size=1), st.integers(min_value=0),
    st.integers(min_value=0), st.text(min_size=1),
)
def test_parser_didnt_match_to_end_raises(subs, fake_idx, fake_hours, garbage):
    srt_blocks = [sub.to_srt() for sub in subs]
    garbage = '\n\n%d\n%d:%s' % (fake_idx, fake_hours, garbage)
    srt_blocks.append(garbage)
    composed = ''.join(srt_blocks)

    with assert_raises(srt.SRTParseError):
        list(srt.parse(composed))
