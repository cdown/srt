[![Linux build status][travis-image]][travis-builds]
[![Windows build status][appveyor-image]][appveyor-builds]
[![Coverage][coveralls-image]][coveralls]
[![Code health][landscape-image]][landscape]
[![Dependencies][requires-image]][requires]

[travis-builds]: https://travis-ci.org/cdown/tinysrt
[travis-image]: https://img.shields.io/travis/cdown/tinysrt/master.svg?label=linux
[appveyor-builds]: https://ci.appveyor.com/project/cdown/tinysrt
[appveyor-image]: https://img.shields.io/appveyor/ci/cdown/tinysrt/master.svg?label=windows
[coveralls]: https://coveralls.io/r/cdown/tinysrt
[coveralls-image]: https://img.shields.io/coveralls/cdown/tinysrt/master.svg
[landscape]: https://landscape.io/github/cdown/tinysrt/master
[landscape-image]: https://landscape.io/github/cdown/tinysrt/master/landscape.svg
[requires]: https://requires.io/github/cdown/tinysrt/requirements/?branch=master
[requires-image]: https://img.shields.io/requires/github/cdown/tinysrt.svg?label=deps

tinysrt is a tiny library for parsing, modifying, and compiling SRT files. It
was created to save myself from the overcomplication and needless abstractions
present in existing SRT libraries for Python.

## Usage

### Parse an SRT to Python objects

```python
>>> subtitle_generator = tinysrt.parse('''\
... 1
... 00:02:17,440 --> 00:02:20,375
... Senator, we're making
... our final approach into Coruscant.
...
... 2
... 00:02:20,476 --> 00:02:22,501
... Very good, Lieutenant.
... ''')
>>> subtitles = list(subtitle_generator)
>>>
>>> subtitles[0].start
datetime.timedelta(0, 137, 440000)
>>> subtitles[1].content
'Very good, Lieutenant.'
```

### Compose an SRT from Python objects

```python
>>> print(tinysrt.compose(subtitles))
1
00:02:17,440 --> 00:02:20,375
Senator, we're making
our final approach into Coruscant.

2
00:02:20,476 --> 00:02:22,501
Very good, Lieutenant.
```

## Installation

tinysrt isn't on PyPi yet. For now, you can download it and run it by itself
(it has no external dependencies).

## Testing

    $ pip install nose
    $ nosetests

## License

tinysrt is licensed under an
[ISC license](http://en.wikipedia.org/wiki/ISC_license). Full information is in
[LICENSE.md](LICENSE.md).
