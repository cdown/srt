#!/usr/bin/env python

import tinysrt
import datetime
from nose.tools import eq_ as eq


def test_parse_time():
    eq(
        datetime.timedelta(hours=1, minutes=2, seconds=3, milliseconds=400),
        tinysrt.parse_time('01:02:03,400'),
    )
