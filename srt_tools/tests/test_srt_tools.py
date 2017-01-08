#!/usr/bin/env python

import os
import subprocess
import tempfile
from nose.tools import assert_true

try:
    from shlex import quote
except ImportError:  # <3.3 fallback
    from shellescape import quote


sample_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')


def run_srt_util(cmd, shell=False, encoding='ascii'):
    raw_out = subprocess.check_output(
        cmd, shell=shell, env={'PYTHONPATH': '.'},
    )
    return raw_out.decode(encoding)


def assert_supports_all_io_methods(cmd):
    cmd = 'srt_tools/' + cmd
    in_file = os.path.join(sample_dir, 'ascii.srt')
    in_file_gb = os.path.join(sample_dir, 'gb2312.srt')
    _, out_file = tempfile.mkstemp()

    outputs = []

    try:
        outputs.append(run_srt_util([cmd, '-i', in_file, '-o', out_file]))
        outputs.append(run_srt_util(
            '%s < %s > %s' % (quote(cmd), quote(in_file), quote(out_file)),
            shell=True,
        ))
        assert_true(len(set(outputs)) == 1)
        run_srt_util(
            [cmd, '-i', in_file_gb, '-o', out_file, '-e', 'gb2312'],
            encoding='gb2312',
        )
    finally:
        os.remove(out_file)


def test_srt_fix_subtitle_ordering():
    assert_supports_all_io_methods('srt-fix-subtitle-indexing')
