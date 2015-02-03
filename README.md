Minecraft Log Analyzer
======================

Analyze the online times of players by scanning `.log.gz` logfiles.
Includes utilities to render GitHub-style punchcards.

Installation
------------

`git clone --recursive https://github.com/Gjum/minecraft-log-analyzer.git`

Usage
-----

`$ ./onlineDay <path/to/logs/> [YYYY-MM-DD = today]`: calculate & display total time each user was online that day (in secs)

`$ ./punchcardDay <path/to/logs/> [YYYY-MM-DD = today]`: draws punchcard of the day into ./punchcardDay.png

`$ ./punchcardCustom <path/to/logs/> <YYYY-MM-DD[-HH]> <YYYY-MM-DD[-HH]>`: draws punchcard of the time range into ./punchcardCustomInterval.png (including start time, excluding end time)

###Remaining to do:

`$ ./punchcardLastHour <path/to/logs/>`: punchcard of the last hour

`$ ./onlineTotal <path/to/logs/>`: total time each user was online ever

Open issues for new use cases.

Example output
--------------

Punchcard:
![punchcard example](https://i.imgur.com/C6Qqvpa.png)

Online times:
```
Udilor:           14333 sec
HHL:              13509 sec
gjum:               375 sec
```
