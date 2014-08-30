Minecraft Log Analyzer
======================

BASH utility to analyze the online times of players by scanning all available `.log.gz` logfiles.
Includes utility to render histograms of generated scanfiles.

Installation
------------

`$ cd YOUR_SERVER_DIR && git clone https://github.com/Gjum/minecraft-log-analyzer.git`

Usage
-----

`$ ./scan-all` to scan all available logs to dayly scanfiles or `$ ./scan-all -f` to force rescan of all files

`$ ./histogram ../path/to/logfile.log.gz.scanned /path/to/list/of/users`

`$ ./histogram-day yyyy-mm-dd`

`$ ./online-today` (for today) or `$ ./online-today YYYY-MM-DD`

`$ ./online-total`

Example output
--------------

When running in a terminal:
(the output also gets colored, not shown here)

```
Tue 12.08.2014 19:00 Moqtah_Laila (1min)
Tue 12.08.2014 20:00 Moqtah_Laila (39min) HHL (55min)
Tue 12.08.2014 21:00 Moqtah_Laila (60min) HHL (60min)
Tue 12.08.2014 22:00 Moqtah_Laila (21min) HHL (21min)
Tue 12.08.2014 23:00 HHL (0min)

Online times:
 8119 seconds or 02:15:19 HHL
 7184 seconds or 01:59:44 Moqtah_Laila
```

---

When piping the output, e.g. to a file:

```
1407862800 Moqtah_Laila 30
1407866400 Moqtah_Laila 2312 HHL 3270
1407870000 Moqtah_Laila 3600 HHL 3600
1407873600 Moqtah_Laila 1242 HHL 1249
1407877200 HHL 0
=== timespans ===
Moqtah_Laila:1407863376-1407863406:1407867688-1407874842
HHL:1407866730-1407874849:1407880587-1407880587
=== onlinetimes ===
Moqtah_Laila 7184
HHL 8119
```

---

Histogram and variants:
(the bars of each user are colored)

```
     Offlinegott |               
            gjum |               
             HHL |    ▇▇ ██ ▂▂ __
    Moqtah_Laila | __ ▅▅ ██ ▂▂   
            time | 19 20 21 22 23

```
