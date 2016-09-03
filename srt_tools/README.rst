srt_tools contains utilities written to process SRT files. All utilities use
the Python srt_ library internally.

.. _srt: https://github.com/cdown/srt

Utilities
---------

- *fix-subtitle-indexing* fixes subtitle indexing. Some badly formed SRT files
  will have indexes that occur in a different order than the starting
  timestamps for the subtitles they are associated with. This makes some media
  players unable to display those subtitles, and they are subsequently lost
  into the ether.
- *fixed-timeshift* does fixed time correction. For example, if you have a
  movie that is consistently out of sync by two seconds, you can run this tool
  to shift the entire subtitle two seconds ahead or behind.
- *linear-timeshift* does linear time correction. If you have a movie that
  runs slower or faster than the subtitle that you have, it will repeatedly
  lose sync. This tool can apply linear time corrections to all subtitles in
  the SRT, resyncing it with the video.
- *lines-matching* takes a function and removes lines that don't return true
  when passed to it. For example, you can keep only lines that contain Chinese
  by installing the hanzidentifier_ package, and running ``srt lines-matching
  -m hanzidentifier -f hanzidentifier.has_chinese < input``.
- *mux* can mux_ multiple subtitles together into one. For example, if you
  have a Chinese subtitle and an English subtitle, and you want to have one
  subtitle file that contains both, this tool can do that for you. It also
  supports clamping subtitles starting or ending at similar times to the same
  time to avoid subtitles jumping around the screen.
- *strip-html* strips HTML formatting from subtitle content. This is especially
  prevalant in `SSA/ASS`_ subtitles that have been directly converted to SRT.

.. _mux: https://en.wikipedia.org/wiki/Multiplexing
.. _`SSA/ASS`: https://en.wikipedia.org/wiki/SubStation_Alpha
.. _hanzidentifier: https://github.com/tsroten/hanzidentifier
