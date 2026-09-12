"""Exercise the actual command-line scripts using synthetic subtitle files."""

from __future__ import unicode_literals

import os
import subprocess
import sys

import pytest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALID = b"1\n00:00:01,000 --> 00:00:02,000\nSynthetic subtitle\n\n"
COMMANDS = [
    ("normalise", []),
    ("deduplicate", []),
    ("fixed-timeshift", ["--seconds", "1"]),
    (
        "linear-timeshift",
        [
            "--f1",
            "00:00:01,000",
            "--t1",
            "00:00:01,000",
            "--f2",
            "00:00:02,000",
            "--t2",
            "00:00:03,000",
        ],
    ),
    ("process", ["-f", "lambda text: text.upper()"]),
    ("lines-matching", ["-f", "lambda text: True"]),
]


def run_tool(name, args):
    launcher = (
        "import sys,runpy; sys.path.insert(0,sys.argv.pop(1)); "
        "runpy.run_path(sys.argv.pop(1),run_name='__main__')"
    )
    command = [
        sys.executable,
        "-c",
        launcher,
        ROOT,
        os.path.join(ROOT, "srt_tools", "srt-" + name),
    ] + args
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


@pytest.mark.parametrize("name,extra", COMMANDS)
def test_inplace_parse_failure_preserves_source(tmpdir, name, extra):
    source = tmpdir.join("invalid.srt")
    original = b"NOT AN SRT FILE\n"
    source.write_binary(original)
    status, _, stderr = run_tool(name, ["-i", str(source), "--inplace"] + extra)
    assert status != 0
    assert b"SRTParseError" in stderr
    assert source.read_binary() == original


@pytest.mark.parametrize("name,extra", COMMANDS)
def test_inplace_matches_stdout_and_file_output(tmpdir, name, extra):
    source = tmpdir.join("valid.srt")
    destination = tmpdir.join("output.srt")
    source.write_binary(VALID)
    status, expected, stderr = run_tool(name, ["-i", str(source)] + extra)
    assert status == 0, stderr
    assert source.read_binary() == VALID
    status, _, stderr = run_tool(
        name, ["-i", str(source), "-o", str(destination)] + extra
    )
    assert status == 0, stderr
    assert destination.read_binary() == expected
    before = os.stat(str(source))
    status, _, stderr = run_tool(name, ["-i", str(source), "--inplace"] + extra)
    assert status == 0, stderr
    assert source.read_binary() == expected
    after = os.stat(str(source))
    assert (before.st_ino, before.st_mode) == (after.st_ino, after.st_mode)


@pytest.mark.parametrize(
    "name,extra,error",
    [
        ("process", ["-f", "lambda text: 1 / 0"], b"ZeroDivisionError"),
        ("lines-matching", ["-f", "lambda text: 1 / 0"], b"ZeroDivisionError"),
        ("fixed-timeshift", ["--seconds", "1e100"], b"OverflowError"),
        (
            "process",
            ["--encoding", "ascii", "-f", "lambda text: text + u'\\u00e9'"],
            b"UnicodeEncodeError",
        ),
    ],
)
def test_inplace_conversion_failure_preserves_source(tmpdir, name, extra, error):
    source = tmpdir.join("valid.srt")
    source.write_binary(VALID)
    status, _, stderr = run_tool(name, ["-i", str(source), "--inplace"] + extra)
    assert status != 0
    assert error in stderr
    assert source.read_binary() == VALID


def test_mux_file_output_matches_stdout(tmpdir):
    source = tmpdir.join("valid.srt")
    destination = tmpdir.join("output.srt")
    source.write_binary(VALID)
    status, expected, stderr = run_tool("mux", ["-i", str(source)])
    assert status == 0, stderr
    status, _, stderr = run_tool("mux", ["-i", str(source), "-o", str(destination)])
    assert status == 0, stderr
    assert destination.read_binary() == expected


@pytest.mark.parametrize("kind", ["link", "symlink"])
def test_inplace_preserves_links(tmpdir, kind):
    target = tmpdir.join("target.srt")
    source = tmpdir.join("source.srt")
    target.write_binary(VALID)
    if not hasattr(os, kind):
        pytest.skip("This Python does not provide os." + kind)
    try:
        getattr(os, kind)(str(target), str(source))
    except OSError as error:
        pytest.skip("Cannot create test link: " + str(error))
    before = os.stat(str(target))
    status, _, stderr = run_tool("normalise", ["-i", str(source), "--inplace"])
    assert status == 0, stderr
    assert target.read_binary() == source.read_binary()
    assert os.stat(str(source)).st_ino == before.st_ino
    assert os.stat(str(target)).st_ino == before.st_ino
    if kind == "symlink":
        assert os.path.islink(str(source))


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16"])
def test_inplace_encoding_matches_stdout(tmpdir, encoding):
    source = tmpdir.join("unicode.srt")
    text = VALID.decode("ascii").replace("Synthetic subtitle", "caf\u00e9")
    source.write_binary(text.encode(encoding))
    args = ["-i", str(source), "--encoding", encoding]
    status, expected, stderr = run_tool("normalise", args)
    assert status == 0, stderr
    status, _, stderr = run_tool("normalise", args + ["--inplace"])
    assert status == 0, stderr
    assert source.read_binary() == expected


def test_inplace_ignore_parsing_errors(tmpdir):
    source = tmpdir.join("recoverable.srt")
    source.write_binary(b"Junk\n" + VALID)
    args = ["-i", str(source), "--ignore-parsing-errors"]
    status, expected, stderr = run_tool("normalise", args)
    assert status == 0, stderr
    status, _, stderr = run_tool("normalise", args + ["--inplace"])
    assert status == 0, stderr
    assert source.read_binary() == expected


def test_inplace_rejects_stdin():
    status, _, stderr = run_tool("normalise", ["--inplace"])
    assert status != 0
    assert b"Cannot use --inplace on stdin" in stderr


def test_inplace_rejects_explicit_output(tmpdir):
    source = tmpdir.join("valid.srt")
    destination = tmpdir.join("output.srt")
    source.write_binary(VALID)
    args = ["-i", str(source), "-o", str(destination), "--inplace"]
    status, _, stderr = run_tool("normalise", args)
    assert status != 0
    assert b"Cannot use -o and -p together" in stderr
    assert source.read_binary() == VALID
    assert not destination.exists()
