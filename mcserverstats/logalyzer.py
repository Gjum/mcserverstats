import glob
import gzip
import errno
from mcserverstats import timeutils
import logging
import os
import re
import yaml

logging.basicConfig(format='[%(levelname)s %(lineno)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger('logalyzer')
logger.setLevel(logging.INFO)

log_actions = []
def log_action(regex_str):
    def inner(fun):
        regex_comp = re.compile(regex_str)
        log_actions.append((regex_comp, fun))
        return fun
    return inner

class LogFile:
    RE_TIME = re.compile('^\[([\d:]{8})\] ')
    RE_START = re.compile('^\[([\d:]{8})\] \[Server thread/INFO\]: Starting minecraft server version ')

    def __init__(self, logs_dir, log_name, prev_log=None):
        self.log_name = log_name
        self.prev_log = prev_log
        self.log_path = os.path.join(logs_dir, log_name + '.log')
        if self.log_name == 'latest':
            # for timestamps in log lines
            self.day_str = timeutils.ensure_day_only(timeutils.latest_log_date_str(logs_dir))
        else:
            self.day_str = self.log_name.rsplit('-', 1)[0]
        self.uuids = {}  # name -> last associated UUID
        self.been_read = False

        self.yaml_attributes = 'started', 'stopped', 'first_event', 'last_event', 'online', 'times'
        self.started = None
        self.stopped = None
        self.first_event = None
        self.last_event = None
        self.online = {}
        self.times = []

    def read_log(self, force_convert=False):
        if self.been_read:
            logger.debug('Already read %s', self.log_name)
            return
        try:
            if force_convert:
                raise Exception  # force re-conversion
            yaml_file = open(self.log_path + '.yaml', 'r')
        except (OSError, IOError) as e:
            if e.errno != errno.ENOENT:
                raise
            # no converted file exists, create it
            self.convert_log(force_convert)
        else:  # converted file exists, read it
            with yaml_file:
                data = yaml.load(yaml_file)
                for attr in self.yaml_attributes:
                    setattr(self, attr, data[attr])
        self.been_read = True
        for attr in self.yaml_attributes:
            logger.debug('%s.%s = %s' % (self.log_name, attr, getattr(self, attr)))
        logger.debug('Done reading %s ------------------------------', self.log_name)

    def convert_log(self, force_convert=False):
        self.peek_start()
        if self.prev_log:
            self.prev_log.read_log(force_convert)
            self.online = self.prev_log.online
            if self.started:
                # TODO crash, update previous yaml instead?
                for name in list(self.online.keys())[:]:
                    self.found_leave(-1, self.prev_log.last_event, name, 'Server Crash')
                    logger.info('Server started, leaving %s at %s' % (name, self.log_name))
        elif not self.started:
            raise ValueError('First log and no server start')
        if self.log_name == 'latest': logger.debug('Converting latest')
        else: logger.info('Converting %s', self.log_name)
        if self.log_name == 'latest':
            log_file = open(self.log_path, 'rb')
        else:
            log_file = gzip.open(self.log_path + '.gz', 'rb')
        with log_file:
            line_no = 0
            for line in log_file:
                if b' [@' == line[32:35]:
                    continue  # ignore command block activity
                logger.debug('[Log %s@%i] %s', self.log_name, line_no, line)
                line_no += 1
                line = line.decode('latin_1')
                time_match = self.RE_TIME.match(line)
                if time_match:  # only look at lines with a timestamp
                    seconds = timeutils.date_str_to_epoch(self.day_str, line[1:9])
                    if self.first_event is None:
                        self.first_event = seconds
                    if self.last_event is None or self.last_event < seconds:
                        self.last_event = seconds
                    line_after_time = line[11:]  # strip off the `[12:34:56] `
                    for regex, action in log_actions:
                        match = regex.match(line_after_time)
                        if match:
                            args = match.groups()
                            logger.debug('Action: %s (%2i %i) %s: %s' % (self.log_name, line_no, seconds, action.__name__, args))
                            action(self, line_no, seconds, *args)
                            break
        if self.stopped:
            for name in list(self.online.keys())[:]:
                self.found_leave(-1, self.last_event, name, 'Server Stop')
                logger.info('Server stopped, leaving %s at %s' % (name, self.log_name))
        self.write_yaml()

    @log_action('^\[User Authenticator #(\d+)/INFO\]: UUID of player ([^ ]+) is ([-\da-f]{36})$')
    def found_uuid(self, line_nr, seconds, auth_nr, name, uuid):
        self.uuids[name] = uuid

    @log_action('^\[Server thread/INFO\]: ([^ \[]+)\[([/\d\.:]+)\] logged in with entity id (\d+) at \(([-\d\.]+), ([-\d\.]+), ([-\d\.]+)\)$')
    def found_join(self, line_nr, seconds, name, ip, e_id, x, y, z):
        if name in self.online:
            logger.warn('Double join %s, at %s %i', name, self.log_name, line_nr)
            self.online[name][2] += 1
        else:
            # support for offline-mode servers, where no UUIDs are announced
            uuid = self.uuids[name] if name in self.uuids else name
            self.online[name] = [uuid, seconds, 1]

    @log_action('^\[Server thread/INFO\]: ([^ ]+) lost connection: (.*)$')
    def found_leave(self, line_nr, seconds, name, reason):
        if "text='You logged in from another location'" in reason:
            logger.info('Double leave "another location" %s, at %s %i', name, self.log_name, line_nr)
        if name not in self.online:
            # TODO look in previous logs for the last leave
            logger.error('Player %s left without joining at %s %i', name, self.log_name, line_nr)
            return  # raise ValueError('Player %s left without joining at %s %i' % (name, self.log_name, line_nr))
        self.online[name][2] -= 1
        uuid, from_sec, num_logins = self.online[name]
        if num_logins == 0:
            del self.online[name]
            self.times.append([uuid, from_sec, seconds, name])
        elif num_logins < 0:
            raise ValueError('Player %s left %ix more often than he joined, at %s %i' % (name, -num_logins, self.log_name, line_nr))

    @log_action('\[Server thread/INFO\]: Stopping server$')
    def found_stop(self, line_nr, seconds):
        if self.stopped:
            logger.error('Stopped two times at %s %i', self.log_name, line_nr)
        self.stopped = True

    def write_yaml(self):
        if self.log_name == 'latest':
            logger.debug('Not writing YAML for latest.log, aborting')
            return
        with open(self.log_path + '.yaml', 'w') as yaml_file:
            logger.debug('Writing %s', self.log_path + '.yaml')
            data = {}
            for attr in self.yaml_attributes:
                data[attr] = getattr(self, attr)
            yaml.dump(data, stream=yaml_file)

    def peek_start(self):
        if self.started is not None:
            # already peeked
            logger.warn('peek_start: Already peeked')
            return self.started
        if self.log_name == 'latest':
            log_file = open(self.log_path, 'rb')
        else:
            log_file = gzip.open(self.log_path + '.gz', 'rb')
        with log_file:
            for line in log_file:
                line = line.decode('latin_1')
                self.started = bool(self.RE_START.match(line))
                if self.started:
                    self.first_event = timeutils.date_str_to_epoch(self.day_str, line[1:9])
                logger.debug('peek_start: In log: %s', self.started)
                return self.started
            self.started = False  # empty log or no start
            logger.error('peek_start: Empty log')
            return self.started


class LogDirectory:
    def __init__(self, logs_dir):
        self.logs_dir = logs_dir
        unsorted_log_names = map(lambda p: os.path.split(p)[1][:-7], glob.iglob(logs_dir + '/*.log.gz'))
        self.sorted_log_name_tuples = sorted(map(self.split_for_compare, unsorted_log_names))
        self.log_files = {}  # log_name_tuple -> LogFile
        prev_log_file = None  # arg for LogFile constructor
        for log_name_tuple in self.sorted_log_name_tuples:
            log_name = self.join_from_compare(log_name_tuple)
            log_file = LogFile(logs_dir, log_name, prev_log_file)
            prev_log_file = log_file
            self.log_files[log_name_tuple] = log_file
        self.log_files['latest'] = LogFile(logs_dir, 'latest', prev_log_file)

    def read_interval_iter(self, from_log=None, to_log=None, inclusive_to=False, force_convert=False):
        """
        Returns an iterator over the LogFiles that lie between `from_log` and `to_log`.
        These are also read and converted if necessary.
        """
        logger.debug('read_interval: from_log=%s to_log=%s', from_log, to_log)
        prev_log = None
        for name_tuple in self.iter_log_name_tuples_between(from_log, to_log, inclusive_to):
            log_file = self.log_files[name_tuple]
            log_file.read_log(force_convert)
            yield log_file
            prev_log = log_file
        if not to_log or not prev_log or prev_log.last_event < timeutils.date_str_to_epoch(to_log):
            log_file = self.log_files['latest']
            log_file.read_log(force_convert)
            yield log_file

    def collect_data(self, from_date=None, to_date=None, inclusive_to=False):
        """
        Returns a tuple of `times` and `online`:
        `times`: a list of all sessions,
        `online`: a map of online players: `player_name -> [uuid, join_time, login_count]`
        """
        from_day, to_day, inclusive_to = self.date_to_log_day(from_date, to_date, inclusive_to)
        times = []
        last_log = None
        for log_file in self.read_interval_iter(from_day, to_day, inclusive_to):
            times.extend(log_file.times)
            last_log = log_file
        return times, (last_log.online if last_log else {})

    def collect_user_sessions(self, from_date=None, to_date=None, inclusive_to=False, whitelist=None):
        t_start = timeutils.date_str_to_epoch(from_date) or float('-inf')
        t_end = timeutils.date_str_to_epoch(to_date or timeutils.latest_log_date_str(self.logs_dir))
        # TODO inclusive_to
        user_sessions = {}  # uuid -> [sessions]

        def crop_and_add(uuid, t_from, t_to, name):
            if whitelist and uuid not in whitelist:
                return
            # crop to interval
            t_from = max(t_from, t_start)
            t_to = min(t_to, t_end)
            if t_from >= t_to:
                return
            # add data to collection
            if uuid not in user_sessions:
                user_sessions[uuid] = []
            user_sessions[uuid].append([uuid, t_from, t_to, name])

        times, online = self.collect_data(from_date, to_date, inclusive_to)
        for uuid, t_from, t_to, name in times:
            crop_and_add(uuid, t_from, t_to, name)
        for name, sess_begin in online.items():
            uuid, t_from = sess_begin[:2]
            crop_and_add(uuid, t_from, t_end, name)
        return user_sessions

    def collect_uptimes(self, from_date=None, to_date=None, inclusive_to=False):
        from_day, to_day, inclusive_to = self.date_to_log_day(from_date, to_date, inclusive_to)
        first_event = None
        for log_file in self.read_interval_iter(from_day, to_day, inclusive_to):
            if log_file.started and log_file.prev_log and not log_file.prev_log.stopped:
                yield (first_event or timeutils.date_str_to_epoch(from_date),
                       log_file.prev_log.last_event)
                first_event = None
            if not first_event:
                first_event = log_file.first_event if log_file.started \
                    else timeutils.date_str_to_epoch(from_date)
            if log_file.stopped:
                yield (first_event, log_file.last_event)
                first_event = None
        if first_event:
            yield (first_event, timeutils.date_str_to_epoch(
                to_date or timeutils.latest_log_date_str(self.logs_dir)))

    def iter_log_name_tuples_between(self, from_log=None, to_log=None, inclusive_to=False):
        """
        from_log, to_log are in format yyyy-mm-dd or yyyy-mm-dd-n,
        from_log may be None to accept all logs before to_log,
        to_log may be None to accept all logs after from_log
        """
        between = self.sorted_log_name_tuples
        if from_log is not None:
            from_split = self.split_for_compare(from_log)
            between = filter(lambda log: from_split <= log[:3], between)
        if to_log is not None:
            to_split = self.split_for_compare(to_log)
            if inclusive_to:
                between = filter(lambda log: log[:3] <= to_split, between)
            else:
                between = filter(lambda log: log[:3] < to_split, between)
        return between

    @staticmethod
    def date_to_log_day(from_date, to_date, inclusive_to=False):
        if to_date and timeutils.date_str_sep in to_date:
            inclusive_to = True
        from_day, to_day = map(timeutils.ensure_day_only, (from_date, to_date))
        return from_day, to_day, inclusive_to

    @staticmethod
    def split_for_compare(log_name):
        return tuple(int(i) for i in log_name.split('-'))

    @staticmethod
    def join_from_compare(log_name_tuple):
        return '%i-%02i-%02i-%i' % log_name_tuple


if __name__ == '__main__':
    test_logs = LogDirectory('test_logs/')
    for user, sessions in test_logs.collect_user_sessions().items():
        print(user)
        for session in sessions:
            print('   ', session)
