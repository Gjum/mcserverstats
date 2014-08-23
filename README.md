Minecraft Log Analyzer
======================

BASH utility to analyze the online times of players by scanning all available `.log.gz` logfiles.
Includes utility to render histograms of generated scanfiles.

Installation
------------

`$ cd YOUR_SERVER_DIR && git clone https://github.com/Gjum/minecraft-log-analyzer.git`

Usage
-----

`$ ./scan-all`

`$ ./histogram ../path/to/logfile.log.gz.scanned /path/to/list/of/users`

Example output
--------------

When running in a terminal:
(the output also gets colored, not shown here)

```
Thu 14.08.2014 00:00 10wwinterb (20min) Offlinegott (48min) fatelrueckler (60min)
Thu 14.08.2014 01:00 10wwinterb (42min) fatelrueckler (60min)
Thu 14.08.2014 02:00 10wwinterb (29min) fatelrueckler (60min)
Thu 14.08.2014 03:00 fatelrueckler (8min)
Thu 14.08.2014 10:00 10wwinterb (16min)
Thu 14.08.2014 11:00 fatelrueckler (59min)
Thu 14.08.2014 12:00 Udilor (6min) fatelrueckler (55min) gjum (32min)
Thu 14.08.2014 13:00 gjum (43min) Udilor (0min)
Thu 14.08.2014 14:00 gjum (26min) 10wwinterb (31min) Offlinegott (18min) Udilor (47min)
Thu 14.08.2014 15:00 gjum (52min) 10wwinterb (58min) Udilor (60min) Offlinegott (55min)
Thu 14.08.2014 16:00 Udilor (3min) 10wwinterb (42min) Offlinegott (58min) gjum (55min) Moqtah_Laila (46min)
Thu 14.08.2014 17:00 gjum (50min) Offlinegott (58min) Moqtah_Laila (60min)
Thu 14.08.2014 18:00 Moqtah_Laila (60min) Offlinegott (33min)
Thu 14.08.2014 19:00 Moqtah_Laila (18min) Offlinegott (60min)
Thu 14.08.2014 20:00 HHL (44min) Offlinegott (59min)
Thu 14.08.2014 21:00 10wwinterb (19min) Offlinegott (58min) HHL (29min)
Thu 14.08.2014 22:00 Offlinegott (55min) gjum (55min) Moqtah_Laila (55min) 10wwinterb (38min) HHL (54min)
Thu 14.08.2014 23:00 Moqtah_Laila (31min) gjum (44min) Offlinegott (49min) 10wwinterb (35min) HHL (54min)

Online times:
33929 seconds or 09:25:29 Offlinegott
21835 seconds or 06:03:55 gjum
20481 seconds or 05:41:21 10wwinterb
18192 seconds or 05:03:12 fatelrueckler
16340 seconds or 04:32:20 Moqtah_Laila
11060 seconds or 03:04:20 HHL
 7185 seconds or 01:59:45 Udilor
```

When piping the output, e.g. to a file:

```
1407967200 10wwinterb 1222 Offlinegott 2939 fatelrueckler 3600
1407970800 10wwinterb 2617 fatelrueckler 3600
1407974400 10wwinterb 1776 fatelrueckler 3600
1407978000 fatelrueckler 538
1408003200 10wwinterb 963
1408006800 fatelrueckler 3544
1408010400 Udilor 443 fatelrueckler 3310 gjum 1930
1408014000 gjum 2644 Udilor 55
1408017600 gjum 1638 10wwinterb 1982 Offlinegott 1111 Udilor 2907
1408021200 gjum 3168 10wwinterb 3530 Udilor 3600 Offlinegott 3375
1408024800 Udilor 180 10wwinterb 2767 Offlinegott 3548 gjum 3443 Moqtah_Laila 2775
1408028400 gjum 3010 Offlinegott 3559 Moqtah_Laila 3600
1408032000 Moqtah_Laila 3600 Offlinegott 2085
1408035600 Moqtah_Laila 1130 Offlinegott 3600
1408039200 HHL 2658 Offlinegott 3596
1408042800 10wwinterb 1142 Offlinegott 3533 HHL 1814
1408046400 Offlinegott 3507 gjum 3314 Moqtah_Laila 3349 10wwinterb 2344 HHL 3291
1408050000 Moqtah_Laila 1886 gjum 2688 Offlinegott 3076 10wwinterb 2138 HHL 3297
=== onlinetimes ===
Udilor 1408053297
10wwinterb 1408053297
gjum 1408053297
Offlinegott 1408053297
fatelrueckler 1408053297
Moqtah_Laila 1408053297
HHL 1408053297
```

Histogram:
(the bars of each user are colored)

```
     Offlinegott | ██                      ▄▄ ██ ██ ██ ▄▄ ██ ██ ██ ██ ██
            gjum |                   ▄▄ ▄▄ ▄▄ ██ ██ ██             ██ ▄▄
             HHL |                                           ▄▄ ▄▄ ██ ██
    Moqtah_Laila |                               ██ ██ ██ ▄▄       ██ ▄▄
            time | 00 01 02 03 10 11 12 13 14 15 16 17 18 19 20 21 22 23
```

