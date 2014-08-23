Minecraft Log Analyzer
======================

BASH utility to analyze the online times of players by scanning all available `.log.gz` logfiles.
Includes utility to render Histograms of generated scanfiles.

Installation
------------

`$ cd YOUR_SERVER_DIR && git clone https://github.com/Gjum/minecraft-log-analyzer.git`

Usage
-----

`$ ./scan-all`
`$ ./histogram ../path/to/logfile.log.gz.scanned /path/to/list/of/usersÂ´Â

Example output
--------------

```
Sat 16.08.2014 18:00 gjum 10wwinterb
Sat 16.08.2014 19:00 HHL 10wwinterb
Sat 16.08.2014 20:00 HHL 10wwinterb gjum Offlinegott
Sat 16.08.2014 21:00 Udilor gjum Offlinegott Moqtah_Laila
Sat 16.08.2014 22:00 10wwinterb HHL gjum Udilor Offlinegott Moqtah_Laila
Sat 16.08.2014 23:00 HHL 10wwinterb gjum Udilor Offlinegott Moqtah_Laila
Sun 17.08.2014 00:00 HHL Offlinegott
```

```
Offlinegott	| ||                      || || || || || || || || || ||
HHL         |                                           || || || ||
gjum	    	|                   || || || || || ||             || ||
time	    	| 00 01 02 03 10 11 12 13 14 15 16 17 18 19 20 21 22 23
```
