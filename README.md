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
Thu 14.08.2014 00:00 Offlinegott 1157 10wwinterb 1222 fatelrueckler 11291
Thu 14.08.2014 01:00 10wwinterb 839 fatelrueckler 11291
Thu 14.08.2014 02:00 10wwinterb 3554 fatelrueckler 11291
Thu 14.08.2014 03:00 fatelrueckler 11291
Thu 14.08.2014 10:00 10wwinterb 963
Thu 14.08.2014 11:00 fatelrueckler 6854
Thu 14.08.2014 12:00 Udilor 354 fatelrueckler 6854 gjum 3237
Thu 14.08.2014 13:00 gjum 3237 Udilor 55
Thu 14.08.2014 14:00 gjum 417 Udilor 845 10wwinterb 147 Offlinegott 3734
Thu 14.08.2014 15:00 gjum 1360 10wwinterb 1948 Offlinegott 3734 Udilor 4606
Thu 14.08.2014 16:00 10wwinterb 1607 Udilor 4606 Offlinegott 1463 gjum 907 Moqtah_Laila 11105
Thu 14.08.2014 17:00 Offlinegott 2694 gjum 3697 Moqtah_Laila 11105
Thu 14.08.2014 18:00 Offlinegott 3195 Moqtah_Laila 11105
Thu 14.08.2014 19:00 Moqtah_Laila 11105 Offlinegott 5154
Thu 14.08.2014 20:00 Offlinegott 5154 HHL 2668
Thu 14.08.2014 21:00 HHL 2668 Offlinegott 4671 10wwinterb 2130
Thu 14.08.2014 22:00 10wwinterb 2130 Offlinegott 2527 HHL 3540 gjum 4398 Moqtah_Laila 5235
Thu 14.08.2014 23:00 Offlinegott 944 gjum 4398 Moqtah_Laila 5235 10wwinterb 3374 HHL 3909

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
1407967200 Offlinegott 1157 10wwinterb 1222 fatelrueckler 11291
1407970800 10wwinterb 839 fatelrueckler 11291
1407974400 10wwinterb 3554 fatelrueckler 11291
1407978000 fatelrueckler 11291
1408003200 10wwinterb 963
1408006800 fatelrueckler 6854
1408010400 Udilor 354 fatelrueckler 6854 gjum 3237
1408014000 gjum 3237 Udilor 55
1408017600 gjum 417 Udilor 845 10wwinterb 147 Offlinegott 3734
1408021200 gjum 1360 10wwinterb 1948 Offlinegott 3734 Udilor 4606
1408024800 10wwinterb 1607 Udilor 4606 Offlinegott 1463 gjum 907 Moqtah_Laila 11105
1408028400 Offlinegott 2694 gjum 3697 Moqtah_Laila 11105
1408032000 Offlinegott 3195 Moqtah_Laila 11105
1408035600 Moqtah_Laila 11105 Offlinegott 5154
1408039200 Offlinegott 5154 HHL 2668
1408042800 HHL 2668 Offlinegott 4671 10wwinterb 2130
1408046400 10wwinterb 2130 Offlinegott 2527 HHL 3540 gjum 4398 Moqtah_Laila 5235
1408050000 Offlinegott 944 gjum 4398 Moqtah_Laila 5235 10wwinterb 3374 HHL 3909
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
     Offlinegott | ▄▄                      ██ ██ ▄▄ ▄▄ ██ ██ ██ ██ ▄▄ __
            gjum |                   ██ ██ __ ▄▄ __ ██             ██ ██
             HHL |                                           ▄▄ ▄▄ ██ ██
    Moqtah_Laila |                               ██ ██ ██ ██       ██ ██
            time | 00 01 02 03 10 11 12 13 14 15 16 17 18 19 20 21 22 23
```

