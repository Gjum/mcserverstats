Minecraft Log Analyzer
======================

Analyze the online times of players on your Minecraft server by scanning the logfiles.

Includes utilities to collect interesting user data and render timelines.

Installation
------------

`git clone https://github.com/Gjum/mc-logalyzer.git`

Usage
-----

`./timelineDay <path to log files> <png_path> [<day> | [<from-day> <to-day>]]`

day format is "YYYY-MM-DD", get times from...

- no days: last 24h,
- `day` only: times during that day,
- `from` and `to`: time between `from` and `to`, `to` is exclusive

`./onlineTimes <path to log files> [<day> | [<from-day> <to-day>]]`

day format is "YYYY-MM-DD", get times from...

- no days: total times,
- `day` only: times during that day,
- `from` and `to`: time between `from` and `to`, `to` is exclusive

### Roadmap

TODO

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
