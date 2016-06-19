=========
srt-tools
=========

srt-tools is a repo containing utilities written to process SRT files. All
utilities use the Python srt_ library internally.

.. _srt: https://github.com/cdown/srt

Utilities
---------

- *chinese-lines-only* removes subtitle lines that don't appear to be
  Chinese. Useful for turning joing English/Chinese subtitles into Chinese
  subtitles only.
- *fix-subtitle-indexing* fixes subtitle indexing. Some badly formed SRT files
  will have indexes that occur in a different order than the starting
  timestamps for the subtitles they are associated with. This makes some media
  players unable to display those subtitles, and they are subsequently lost
  into the ether.
- *linear-timeshift* does linear time correction. If you have a movie that
  runs slower or faster than the subtitle that you have, it will repeatedly
  lose sync. This tool can apply linear time corrections to all subtitles in
  the SRT, resyncing it with the video.
- *mux-subs* can mux_ multiple subtitles together into one. For example, if you
  have a Chinese subtitle and an English subtitle, and you want to have one
  subtitle file that contains both, this tool can do that for you. It also
  supports clamping subtitles starting or ending at similar times to the same
  time to avoid subtitles jumping around the screen.
- *strip-html* strips HTML formatting from subtitle content. This is especially
  prevalant in `SSA/ASS`_ subtitles that have been directly converted to SRT.

.. _mux: https://en.wikipedia.org/wiki/Multiplexing
.. _`SSA/ASS`: https://en.wikipedia.org/wiki/SubStation_Alpha
