import os
import gzip
import datetime
import time
from glob import glob

"""
Wanted functionality:
    - DONE time played today per player
    - DONE total time played per player
    - DONE histogram of all players
TODO respect PEP
TODO convert exceptions into assumptions and stdErr message
an interesting line: (? = 0xa7, color code escape char)
    [18:18:10] [Server thread/INFO]: ?6HHL?r left the game
    012345678901234567890123456789012345678901234567890123
    0         1         2         3         4         5
"""

stillOnline = '?'
#stillOnline = float("inf") # TODO

def getDateFromFile(filename, daytime = '00:00:00'):
    day = os.path.basename(filename)[:10] # "path/to/2014-12-01-2.log.gz" -> "2014-12-01"
    if day == 'latest.log':
        day = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(filename)))
    dateString = day + ' ' + daytime
    epoch = int(time.mktime(datetime.datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S').timetuple()))
    return epoch, dateString

def getPreviousLog(argLogPath): # TODO untested, unused
    """Finds the logfile that was created before argLogPath.
    Only works when all files are in one directory.
    """
    logDir = os.path.dirname(argLogPath)
    argLog = os.path.basename(argLogPath)
    # note that '1234-56-78.log.gz' < 'latest.log'
    prevLog = '0000-00-00-0.log.gz'
    for logPath in glob(logDir + '/*.log.gz'):
        log = os.path.basename(logPath)
        if prevLog < log < argLog:
            prevLog = log
    return prevLog

class LogProcessor:
    def __init__(self):
        self.times = {} # online times: dictionary of players with one array of join/leave time pairs per player
        self.processedFiles = [] # files that were processed
        self.firstEvent = None
        self.lastEvent = None

    def processFile(self, filename):
        """Reads all info from a file, might be ascii or gzip format.
        Opens older files in the same directory if needed (see special case #2/#3).
        Creates self.times, a dict of players with join/leave times.
        """
        opener = gzip.open if filename[-3:] == '.gz' else open
        with opener(filename) as logfile:
            line = logfile.readline()
            if not line:
                raise ValueError('Empty log file')
            actionTime, _ = getDateFromFile(filename, line[1:9].decode())
            self.firstEvent = actionTime if self.firstEvent is None else min(self.firstEvent, actionTime)
            # first line might be '[12:34:56] [Server thread/INFO]: Starting minecraft server version 1.8.1'
            freshRestart = line[12:59] == b'Server thread/INFO]: Starting minecraft server '
            if not freshRestart:
                logfile.seek(0) # first line might already contain joined/left information
            for line in logfile:
                # actionTime: seconds since epoch when the event occurred, localtime
                actionTime, dateString = getDateFromFile(filename, line[1:9].decode())
                # '<' and '*': skip chat
                if line[-10:] == b' the game\n' and line[33] != b'<' and line[33] != b'*' and line[12:33] == b'Server thread/INFO]: ':
                    # line contains joined/left information, extract it
                    split = line.split()
                    player = split[-4]
                    if player[0] == b'\xa7':
                        player = player[2:-2] # remove color codes
                    player = player.decode().encode('ascii')
                    action = split[-3].decode()
                    # save information
                    # TODO special cases:
                    #   - join w/o leave: player joins with another instance before the old instance leaves
                    #   - leave w/o join: new day, new logfile, but server was not restarted and players are still online
                    #   - invisible online players: latest.log: players might have logged in yesterday and still be online
                    if player not in self.times:
                        self.times[player] = [] # add empty entry for player
                    if action == 'joined':
                        # TODO special cases should be handled here
                        if len(self.times[player]) > 0 and self.times[player][-1][1] == stillOnline:
                            raise NotImplementedError('Double join') # TODO no error in special case #1
                        self.times[player].append((actionTime, stillOnline))
                    elif action == 'left':
                        # TODO special cases should be handled here
                        # we assume that if a player is online, the newest times[player] entry is (#, stillOnline)
                        if self.times[player] and self.times[player][-1][1] == stillOnline: # player is online
                            self.times[player][-1] = (self.times[player][-1][0], actionTime) # just add missing leave time
                        else: # player seems to not be online
                            if freshRestart:
                                raise ValueError('Player %s left without logging in after fresh server restart\n    in %s at %s' % (player, filename, dateString))
                                # TODO check previous logs for when player joined
                    else:
                        raise ValueError('Invalid action: %s %s the game\n    in %s at %s' % (player, action, filename, dateString))
            self.lastEvent = max(self.lastEvent, actionTime)
            self.processedFiles.append(filename)

    def getSlots(self, slotSize = 3600):
        # if this throws an error, check if self.times is filled
        startSlot = self.firstEvent // slotSize
        endSlot = self.lastEvent // slotSize
        numSlots = endSlot - startSlot + 1
        slots = [{} for _ in range(numSlots)]
        for player, playerTimes in self.times.items():
            for joinTime, leaveTime in playerTimes:
                if leaveTime == stillOnline:
                    leaveTime = self.lastEvent
                for slotNum in range(joinTime // slotSize, leaveTime // slotSize + 1):
                    slotIndex = slotNum - startSlot # position in list
                    if slotIndex < 0:
                        raise ValueError('Negative slot index')
                    if slotIndex >= numSlots:
                        raise ValueError('Slot index too large')
                    if player not in slots[slotIndex]:
                        slots[slotIndex][player] = 0
                    slotTime = slotNum * slotSize # begin time of current slot in seconds since epoch
                    playStart = max(joinTime, slotTime)
                    playEnd = min(leaveTime, slotTime + slotSize)
                    playTime = playEnd - playStart # seconds the player played during current slot
                    slots[slotIndex][player] += int(playTime)
        return startSlot * slotSize, slots

    def printTotalTimes(self, after = 0, before = float('inf')):
        total = {}
        for player, playerTimes in self.times.items():
            total[player] = 0
            for joinTime, leaveTime in playerTimes:
                if leaveTime < after:
                    continue
                if leaveTime == stillOnline:
                    leaveTime = self.lastEvent
                # trim to time interval
                if joinTime < after:
                    joinTime = after
                if leaveTime > before:
                    leaveTime = before
                if joinTime < leaveTime:
                    total[player] += leaveTime - joinTime
        # sort by time in descending order
        for player, playedTime in sorted(total.items(), key=lambda x: x[1], reverse=True):
            print('%-16s %6i sec' % (player+':', playedTime))

    def drawHistogram(self, after = None, before = None, slotSize = 3600):
        # if not provided, show last day
        if after is None:
            after, _ = getDateFromFile(max(self.processedFiles))
        # if not provided, show one day
        if before is None:
            before = after + 3600*24
        print('after, before', after, before)
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
            if slotStartTime + i*slotSize < after:
                continue
            if slotStartTime + i*slotSize >= before:
                continue
            for player in slot.keys():
                if player not in lines:
                    lines[player] = skippedSpace # new player found
            for player in lines.keys():
                onlineTimeInSlot = slot[player] if player in slot else 0
                lines[player] += ' ' + 2*bars[onlineTimeInSlot * numBars // (slotSize+1)] if onlineTimeInSlot > 0 else '   '
            skippedSpace += '   '
            # timeline
            slotTime = i * slotSize + slotStartTime
            timeline += datetime.datetime.fromtimestamp(slotTime).strftime(' %H')
        print(timeline)
        for player, line in lines.items():
            print('')
            print('%-16s%s' % (player, line))


# TODO should go into own script file
def printOnlineTimesLastHour(logPath = '../logs/'):
    processor = LogProcessor()
    processor.processFile(logPath + '/latest.log')
    processor.printTotalTimes()

if __name__ == '__main__':
    processor = LogProcessor()
    processor.processFile('../logs/2014-12-10-1.log.gz')
    processor.processFile('../logs/2014-12-11-1.log.gz')
    processor.processFile('../logs/latest.log')
    print('raw slots:')
    slotStartTime, slots = processor.getSlots()
    for i, slot in enumerate(slots):
        slotTime = i * 3600 + slotStartTime
        formattedTime = datetime.datetime.fromtimestamp(slotTime).isoformat(' ')
        print(formattedTime, slot)
    print('')
    print('total times played per player:')
    processor.printTotalTimes()
    print('')
    print('times played today per player:')
    lastDay, _ = getDateFromFile(max(processor.processedFiles))
    processor.printTotalTimes(lastDay)
    print('')
    print('times played last hour per player:')
    printOnlineTimesLastHour()
    print('')
    print('histogram, last day:')
    processor.drawHistogram()
    print('')
    print('histogram, complete:')
    processor.drawHistogram(processor.firstEvent, processor.lastEvent)
    print('')
    print('histogram, custom interval:')
    processor.drawHistogram(lastDay + 13*3600, lastDay + 22*3600)
