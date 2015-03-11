from copy import deepcopy
import os
import gzip
import datetime
import time
from glob import glob

"""
TODO respect PEP
TODO convert exceptions into assumptions and stdErr message
an interesting line: (? = 0xa7, color code escape char)
    [18:18:10] [Server thread/INFO]: ?6HHL?r left the game
    012345678901234567890123456789012345678901234567890123
    0         1         2         3         4         5
"""

stillOnline = '?'
#stillOnline = float("inf") # TODO
doubleJoin = '!'

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

def joinDicts(dicA, dicB):
    for k, v in dicB.iteritems():
        if k in dicA.data:
            dicA[k] += dicB[k]
        else:
            dicA[k] = deepcopy(v)
    return dicA

class LogProcessor:
    def __init__(self):
        self.times = {} # online times: dictionary of players with one array of join/leave time pairs per player
        self.processedFiles = [] # files that were processed
        self.firstEvent = None
        self.lastEvent = None

    def processFile(self, filename):
        """Reads all info from a file, might be ascii or gzip format.
        Opens older files in the same directory if needed.
        Creates/updates self.times, a dict of players with join/leave times.
        """
        self.times = self.processFileSafe(filename)

    def processFileSafe(self, filename):
        print('Processing', filename)
        opener = gzip.open if filename[-3:] == '.gz' else open
        with opener(filename) as logfile:
            line = logfile.readline()
            if not line:
                raise ValueError('Empty log file')
            action_time, _ = getDateFromFile(filename, line[1:9].decode())
            self.firstEvent = action_time if self.firstEvent is None else min(self.firstEvent, action_time)
            # first line might be '[12:34:56] [Server thread/INFO]: Starting minecraft server version 1.8.1'
            fresh_restart = line[12:59] == b'Server thread/INFO]: Starting minecraft server '
            if not fresh_restart:
                logfile.seek(0)  # first line might already contain joined/left information
            new_times = {}
            for line in logfile:
                # action_time: seconds since epoch when the event occurred, localtime
                try:
                    action_time, date_string = getDateFromFile(filename, line[1:9].decode())
                except ValueError:
                    continue  # ignore line
                # '<' and '*': skip chat
                if line[-10:] == b' the game\n' and line[33] != b'<' and line[33] != b'*' and line[12:33] == b'Server thread/INFO]: ':
                    print line
                    # line contains joined/left information, extract it
                    split = line.split()
                    player = split[-4]
                    if player[0] == b'\xa7':
                        player = player[2:-2]  # remove color codes
                    player = player.decode().encode('ascii')
                    action = split[-3].decode()
                    # save information
                    # TODO special cases:
                    #   - Done: join w/o leave: player joins with another instance before the old instance leaves
                    #   - Done: leave w/o join: new day, new logfile, but server was not restarted and players are still online
                    #   - invisible online players: latest.log: players might have logged in yesterday and still be online
                    if player not in new_times:
                        new_times[player] = []  # add empty entry for player
                    if action == 'joined':
                        # TODO special cases should be handled here
                        if len(new_times[player]) > 0 and new_times[player][-1][1] == stillOnline:
                            new_times[player][-1] = (new_times[player][-1][0], doubleJoin) # mark for next leave
                        elif len(new_times[player]) > 0 and new_times[player][-1][1] == doubleJoin:
                            raise NotImplementedError('Multi-join more than 2 levels deep')
                        else:
                            new_times[player].append((action_time, stillOnline))
                    elif action == 'left':
                        # TODO special cases should be handled here
                        # we assume that if a player is online, the newest times[player] entry is (#, stillOnline) or (#, doubleJoin)
                        if new_times[player] and new_times[player][-1][1] == stillOnline: # player is online
                            new_times[player][-1] = (new_times[player][-1][0], action_time) # just add missing leave time
                        elif new_times[player] and new_times[player][-1][1] == doubleJoin: # player joined twice, ...
                            new_times[player][-1] = (new_times[player][-1][0], stillOnline) # next == second leave finishes ontime entry
                        else: # player seems to not be online
                            if fresh_restart:
                                raise ValueError('Player %s left without logging in after fresh server restart\n    in %s at %s' % (player, filename, date_string))
                            else: # player joined in earlier log
                                oldtimes = self.processFileSafe(getPreviousLog(filename))
                                if not oldtimes[player] or oldtimes[player][-1][1] != stillOnline:
                                    raise NotImplementedError('We need to go deeper') # TODO join not found in previous log, we need recursion
                                oldtimes[player][-1] = (oldtimes[player][-1][0], action_time) # just add missing leave time
                                new_times = joinDicts(oldtimes, new_times)
                    else:
                        raise ValueError('Invalid action: %s %s the game\n    in %s at %s' % (player, action, filename, date_string))
            self.lastEvent = max(self.lastEvent, action_time)
            self.processedFiles.append(filename)
            print('Processed', filename)
            return new_times

    def get_slots(self, slot_size=3600):
        # if this throws an error, check if self.times is filled
        startSlot = self.firstEvent // slot_size
        endSlot = self.lastEvent // slot_size
        numSlots = endSlot - startSlot + 1
        slots = [{} for _ in range(numSlots)]
        for player, playerTimes in self.times.items():
            for joinTime, leaveTime in playerTimes:
                if leaveTime == stillOnline:
                    leaveTime = self.lastEvent
                for slotNum in range(joinTime // slot_size, leaveTime // slot_size + 1):
                    slotIndex = slotNum - startSlot # position in list
                    if slotIndex < 0:
                        raise ValueError('Negative slot index')
                    if slotIndex >= numSlots:
                        raise ValueError('Slot index too large')
                    if player not in slots[slotIndex]:
                        slots[slotIndex][player] = 0
                    slotTime = slotNum * slot_size # begin time of current slot in seconds since epoch
                    playStart = max(joinTime, slotTime)
                    playEnd = min(leaveTime, slotTime + slot_size)
                    playTime = playEnd - playStart # seconds the player played during current slot
                    slots[slotIndex][player] += int(playTime)
        return startSlot * slot_size, slots

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

    def getPunchcard(self, imagePath, after = None, before = None, slotSize = 3600, title = None, slotTimeFormatString = '%H'):
        slotStartTime, slots = self.get_slots(slotSize)
        if len(slots) <= 0:
            print('Error: No data during interval, no punchcard generated' % ())
            return
        # if not provided, show last day
        if after is None:
            after, _ = getDateFromFile(max(self.processedFiles))
        # if not provided, show one day
        if before is None:
            before = after + 3600*24
        playerSlots = {}
        skippedSlots = []
        slotTimes = []
        for i, slot in enumerate(slots):
            if slotStartTime + i*slotSize < after:
                continue
            if slotStartTime + i*slotSize >= before:
                continue
            for player in slot.keys():
                if player not in playerSlots:
                    playerSlots[player] = list(skippedSlots) # new player found
            for player in playerSlots.keys():
                playerSlots[player].append(slot[player] if player in slot else 0)
            skippedSlots.append(0)
            slotTime = i * slotSize + slotStartTime
            slotTimes.append(datetime.datetime.fromtimestamp(slotTime).strftime(slotTimeFormatString))
        if title is None:
            title = datetime.datetime.fromtimestamp(slotStartTime).strftime('%Y-%m-%d')
        from Punchcard import punchcard
        print(imagePath, playerSlots.values(), playerSlots.keys(), slotTimes, title)
        punchcard.punchcard(imagePath, playerSlots.values(), playerSlots.keys(), slotTimes, title=title)

if __name__ == '__main__':
    processor = LogProcessor()
    processor.processFile('../logs/2014-12-10-1.log.gz')
    processor.processFile('../logs/2014-12-11-1.log.gz')
    processor.processFile('../logs/latest.log')
    print('raw slots:')
    slotStartTime, slots = processor.get_slots()
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
    print('punchcard, last day: see punchcard_lastDay.png')
    processor.getPunchcard('punchcard_lastDay.png')
    print('')
    print('punchcard, complete: see punchcard_complete.png')
    processor.getPunchcard('punchcard_complete.png', processor.firstEvent, processor.lastEvent, title='Complete history')
    print('')
    print('punchcard, custom interval: see punchcard_customInterval.png')
    processor.getPunchcard('punchcard_customInterval.png', lastDay + 13*3600, lastDay + 22*3600)
