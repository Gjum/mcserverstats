Minecraft Log Analyzer
======================

Analyze the online times of players by scanning `.log.gz` logfiles.
Includes utilities to render GitHub-style punchcards.

Installation
------------

`git clone --recursive https://github.com/Gjum/minecraft-log-analyzer.git`

Usage
-----

Not much implemented yet...

###Wishlist:

`$ ./punchcardLastHour <path/to/logs/>`: punchcard of the last hour

`$ ./punchcardDay <path/to/logs/> [YYY-MM-DD = today]`: punchcard of the day

`$ ./onlineDay <path/to/logs/> [YYYY-MM-DD = today]`: total time each user was online that day

`$ ./onlineTotal <path/to/logs/>`: total time each user was online ever

Open issues for new use cases.

Example output
--------------

Punchcard:
![punchcard example](https://i.imgur.com/C6Qqvpa.png)

Online times:
```
 8119 seconds or 02:15:19 HHL
 7184 seconds or 01:59:44 Moqtah_Laila
```

Slots:
```
Tue 12.08.2014 19:00 Moqtah_Laila (1min)
Tue 12.08.2014 20:00 Moqtah_Laila (39min) HHL (55min)
Tue 12.08.2014 21:00 Moqtah_Laila (60min) HHL (60min)
Tue 12.08.2014 22:00 Moqtah_Laila (21min) HHL (21min)
Tue 12.08.2014 23:00 HHL (0min)
```

