Minecraft Server Stats
======================

Analyze the online times of players on your Minecraft server by scanning the logfiles.

Includes utilities to collect interesting user data and render timelines.

Installation
------------

`git clone https://github.com/Gjum/mc-server-stats.git`

Usage
-----

`./timelineDay <path/to/logs> <png_path> [<from-date> [to-date]]`

date format is "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS", get timeline from...

- no dates: the 24h before the last log event,
- `from` only: the 24h after that date,
- `from` and `to`: time between `from` and `to`, `to` is exclusive

`./onlineTimes <path/to/logs> [<from-date> [to-date]]`

date format is "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS", get times from...

- no dates: total times,
- `from` only: the 24h after that date,
- `from` and `to`: time between `from` and `to`, `to` is exclusive

### Roadmap

- Timeline: HTML output
- more stats, like
  - times died
  - achievements
- last in-game activity (chat, kills, ...)

[Open an issue](issues/new) for a new use case.

### Testing

Before running the tests, make sure the log files are compressed:

    gzip -k test_logs/2*.log

Also make sure `latest.log` was not modified recently:

    touch -t 01042000 test_logs/latest.log

Example output
--------------

Online times:

    HHL:             160372s or   1 day, 20:32:52
    Offlinegott:     135802s or   1 day, 13:43:22
    Gjum:            129754s or   1 day, 12:02:34
    Udilor:           61365s or          17:02:45
    Ulexos:           33557s or           9:19:17

Timeline:

TODO Image
