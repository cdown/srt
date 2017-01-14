#!/usr/bin/env python

import os
import subprocess
import tempfile
from nose.tools import assert_true
from nose_parameterized import parameterized

try:
    from shlex import quote
except ImportError:  # <3.3 fallback
    from shellescape import quote


sample_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'files')

if os.name == 'nt':
    # Sigh, shlex.quote quotes incorrectly on Windows
    quote = lambda x: x

    # Comes from appveyor
    cur_path = os.environ['PATH']
    python_path = os.environ.get('PYTHON')
    if python_path:
        new_path = r'{py};{py}\Scripts;{path}'.format(
            py=python_path, path=cur_path,
        )
        os.environ['PATH'] = new_path


def run_srt_util(cmd, shell=False, encoding='ascii'):
    raw_out = subprocess.check_output(
        cmd, shell=shell, env={'PYTHONPATH': '.'},
    )
    return raw_out.decode(encoding)


def assert_supports_all_io_methods(cmd, exclude_output=False,
                                   exclude_stdin=False):
    cmd[0] = 'srt_tools/' + cmd[0]

    if os.name == 'nt':
        cmd.insert(0, 'python')

    in_file = os.path.join(sample_dir, 'ascii.srt')
    in_file_gb = os.path.join(sample_dir, 'gb2312.srt')
    fd, out_file = tempfile.mkstemp()

    # This is accessed by filename, not fd
    os.close(fd)

    outputs = []
    cmd_string = ' '.join(quote(x) for x in cmd)

    try:
        outputs.append(run_srt_util(cmd + ['-i', in_file]))
        if not exclude_stdin:
            outputs.append(run_srt_util(
                '%s < %s' % (cmd_string, quote(in_file)),
                shell=True,
            ))
        if not exclude_output:
            run_srt_util(cmd + ['-i', in_file, '-o', out_file])
            run_srt_util(
                cmd + ['-i', in_file_gb, '-o', out_file, '-e', 'gb2312'],
                encoding='gb2312',
            )
            if not exclude_stdin:
                run_srt_util(
                    '%s < %s > %s' % (
                        cmd_string, quote(in_file), quote(out_file),
                    ),
                    shell=True,
                )
        assert_true(len(set(outputs)) == 1, repr(outputs))
    finally:
        os.remove(out_file)


@parameterized([
    (['srt-fix-subtitle-indexing'], False),
    (['srt-fixed-timeshift', '--seconds', '5'], False),
    ([
        'srt-linear-timeshift',
        '--f1', '00:00:01,000',
        '--f2', '00:00:02,000',
        '--t1', '00:00:03,000',
        '--t2', '00:00:04,000',
    ], False),
    (['srt-lines-matching', '-f', 'lambda x: True'], False),
    (['srt-mux'], False, True),
    (['srt-strip-html'], False),

    # Need to sort out time/thread issues
    # (('srt-play'), True),
])
def test_tools_support(args, exclude_output=False, exclude_stdin=False):
    assert_supports_all_io_methods(args, exclude_output, exclude_stdin)
