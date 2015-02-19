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

tinysrt is a tiny library for parsing, modifying, and composing SRT files.

## Usage

### Parse an SRT to Python objects

```python
>>> subtitle_generator = tinysrt.parse('''\
... 421
... 00:31:37,894 --> 00:31:39,928
... OK, look, I think I have a plan here.
...
... 422
... 00:31:39,931 --> 00:31:41,931
... Using mainly spoons,
...
... 423
... 00:31:41,933 --> 00:31:43,435
... we dig a tunnel under the city and release it into the wild.
...
... ''')
>>> subtitles = list(subtitle_generator)
>>>
>>> subtitles[0].start
datetime.timedelta(0, 1897, 894000)
>>> subtitles[1].content
'Using mainly spoons,'
```

### Compose an SRT from Python objects

```python
>>> print(tinysrt.compose(subtitles))
421
00:31:37,894 --> 00:31:39,928
OK, look, I think I have a plan here.

422
00:31:39,931 --> 00:31:41,931
Using mainly spoons,

423
00:31:41,933 --> 00:31:43,435
we dig a tunnel under the city and release it into the wild.

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
