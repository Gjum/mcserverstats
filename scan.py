import os
import gzip
import datetime
from time import mktime
from glob import glob

"""
Wanted functionality:
    - DONE time played today per player
    - DONE total time played per player
    - DONE histogram of all players
TODO special cases:
    - player joins with another instance: new instance joins before old instance leaves
    - new day, but server was not restarted, so players might leave w/o joining
    - latest.log: players might have logged in yesterday and be still online
an interesting line: (? = 0xa7, color code escape char)
    [18:18:10] [Server thread/INFO]: ?6HHL?r left the game
    012345678901234567890123456789012345678901234567890123
    0         1         2         3         4         5
"""

def getDateFromFile(filename, time = '00:00:00'):
    day = os.path.basename(filename)[:10] # "path/to/2014-12-01-2.log.gz" -> "2014-12-01"
    dateString = day + ' ' + time
    time = int(mktime(datetime.datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S').timetuple()))
    return time, dateString

class LogProcessor:
    times = {} # online times: dictionary of players with one array of join/leave time pairs per player
    processedFiles = [] # files that were processed (basename only)

    def getPreviousLog(self, argLogPath): # TODO untested, unused
        """finds the logfile that was created before argLogPath
        only works when all files are in one directory
        """
        logDir = os.path.dirname(argLogPath)
        argLog = os.path.basename(argLogPath)
        prevLog = '0000-00-00-0.log.gz'
        for logPath in glob(logDir + '/*.log.gz'):
            log = os.path.basename(logPath)
            if log < argLog and log > prevLog:
                prevLog = log
        return prevLog

    def processFile(self, filename):
        """reads all info from a file
        opens older files if needed (special case #2/#3)
        returns a dict of players with join/leave times
        """
        logfile = gzip.open(filename)
        try:
            line = logfile.readline()
            if not line: raise ValueError('Empty log file')
            # first line might be '[12:34:56] [Server thread/INFO]: Starting minecraft server version 1.8.1'
            freshRestart = line[12:59] == 'Server thread/INFO]: Starting minecraft server '
            while line:
                # '<' and '*': skip chat
                if line[-10:] == b' the game\n' and line[33] != b'<' and line[33] != b'*' and line[12:33] == b'Server thread/INFO]: ':
                    # line contains joined/left information, extract it
                    # atime: seconds since epoch when the event occured, localtime
                    atime, dateString = getDateFromFile(filename, line[1:9].decode())
                    split = line.split()
                    player = split[-4]
                    if player[0] == b'\xa7': player = player[2:-2] # remove color codes
                    print(player)
                    player = player.decode().encode('ascii')
                    action = split[-3].decode()
                    # save information
                    if player not in self.times: self.times[player] = [] # add empty entry for player
                    if action == 'joined':
                        # TODO special cases should be handled here
                        if len(self.times[player]) > 0 and self.times[player][-1][1] == '?':
                            raise ValueError('Double join') # TODO no error in special case #1
                        self.times[player].append((atime, '?'))
                    elif action == 'left':
                        # TODO special cases should be handled here
                        if self.times[player] and self.times[player][-1][1] == '?': # player is online
                            self.times[player][-1] = (self.times[player][-1][0], atime) # just add missing leave time
                        else: # player seems to not be online
                            if freshRestart: raise ValueError('Player %s left without logging in after fresh server restart\n    in %s at %s' % (player, filename, dateString))
                            # TODO check previous logs when player joined
                    else: raise ValueError('Invalid action: %s %s the game\n    in %s at %s' % (player, action, filename, dateString))
                line = logfile.readline()
        finally:
            logfile.close()
        self.processedFiles.append(os.path.basename(filename))

    def getSlots(self, slotSize = 3600):
        # if this throws an error, check if self.times is filled
        startSlot = int(min(ptimes[0][0] for ptimes in self.times.values())) // slotSize
        endSlot = int(max(ptimes[-1][1] for ptimes in self.times.values())) // slotSize
        numSlots = endSlot - startSlot + 1
        slots = [{} for i in range(numSlots)]
        for player, ptimes in self.times.items():
            for jtime, ltime in ptimes:
                for slotNum in range(jtime // slotSize, ltime // slotSize + 1):
                    slotIndex = slotNum - startSlot # position in list
                    slotTime = slotNum * slotSize # begin time of current slot in seconds since epoch
                    if slotIndex < 0: raise ValueError('Negative slot index')
                    if slotIndex >= numSlots: raise ValueError('Slot index too large')
                    if player not in slots[slotIndex]: slots[slotIndex][player] = 0
                    playStart = max(jtime, slotTime)
                    playEnd = min(ltime, slotTime + slotSize)
                    playTime = playEnd - playStart # seconds the player played during current slot
                    slots[slotIndex][player] += int(playTime)
        return startSlot * slotSize, slots

    def printTotalTimes(self, after = 0, before = float('inf')):
        total = {}
        for player, ptimes in self.times.items():
            total[player] = 0
            for jtime, ltime in ptimes:
                if ltime < after: continue
                # trim to time interval
                if jtime < after: jtime = after
                if ltime > before: ltime = before
                total[player] += max(0, ltime - jtime)
        # sort by time in descending order
        for player, ptime in sorted(total.items(), key=lambda x: x[1], reverse=True):
            print('%-16s %6i sec' % (player+':', ptime))

    def drawHistogram(self, after = None, before = None, slotSize = 3600):
        # if not provided, show last day
        if after is None: after = getDateFromFile(max(self.processedFiles))[0]
        # if not provided, show one day
        if before is None: before = after + 3600*24
        # unicode bars: '_' < 1/8, '\xe2\x96\x81' = 1/8, '\xe2\x96\x88' = 8/8
        # TODO directly use unicode: \u2581, \u2582, ...
        bars = ['_'] + [b'\xe2\x96' + chr(0x80 + i) for i in range(1, 9)]
        numBars = len(bars)
        lines = {}
        skippedSpace = ''
        slotStartTime, slots = self.getSlots(slotSize)
        #slots = slots[(after-slotStartTime) // slotSize:(before-slotStartTime) // slotSize]
        timeline = '%-16s' % datetime.datetime.fromtimestamp(slotStartTime).strftime('%Y-%m-%d')
        for i, slot in enumerate(slots):
            if slotStartTime + i*slotSize < after: continue
            if slotStartTime + i*slotSize >= before: continue
            for player in slot.keys():
                if player not in lines: lines[player] = skippedSpace # new player found
            for player in lines.keys():
                ontime = slot[player] if player in slot else 0
                lines[player] += ' ' + 2*bars[ontime * numBars // (slotSize+1)] if ontime > 0 else '   '
            skippedSpace += '   '
            # timeline
            slotTime = i * slotSize + slotStartTime
            timeline += datetime.datetime.fromtimestamp(slotTime).strftime(' %H')
        print(timeline)
        for player, line in lines.items():
            print('')
            print('%-16s%s' % (player, line))


if __name__ == '__main__':
    processor = LogProcessor()
    processor.processFile('../logs/2014-12-10-1.log.gz')
    processor.processFile('../logs/2014-12-11-1.log.gz')
    print('raw slots:')
    slotStartTime, slots = processor.getSlots()
    for i, slot in enumerate(slots):
        slotTime = i * 3600 + slotStartTime
        formattedTime = datetime.datetime.fromtimestamp(slotTime).isoformat(' ')
        print(formattedTime, slot)
    print('')
    print('total time played:')
    processor.printTotalTimes()
    print('')
    print('time played today:')
    lastDay, _ = getDateFromFile(max(processor.processedFiles))
    processor.printTotalTimes(lastDay)
    print('')
    print('histogram, complete:')
    processor.drawHistogram()
    print('histogram, custom interval:')
    processor.drawHistogram(lastDay + 13*3600, lastDay + 22*3600)

