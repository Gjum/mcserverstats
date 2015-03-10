import glob
import gzip
import datetime
import time
import os
import re
import yaml


YAML_ATTRS = ('started', 'stopped', 'first_event', 'last_event', 'online', 'times')
RE_START = re.compile('^\[[0-9:]{8}\] \[Server thread/INFO\]: Starting minecraft server version ')
RE_TIME = re.compile('^\[([0-9:]{8})\] ')


def date_str_to_epoch(day_str, time_str='00:00:00'):
    epoch = int(time.mktime(datetime.datetime.strptime(day_str + ' ' + time_str, '%Y-%m-%d %H:%M:%S').timetuple()))
    return epoch


class LogTime:
    def __init__(self, data_array):
        self.uuid, self.name, self.t_from = data_array[:3]
        self.t_to = -1 if len(data_array) <= 3 else data_array[3]

    def to_array(self):
        arr = [self.uuid, self.name, self.t_from]
        if self.t_to != -1:
            arr.append(self.t_to)
        return arr

    def is_still_online(self):
        return self.t_to == -1


class LogFile:
    def __init__(self, logs_dir, log_name='latest'):
        self.log_name = log_name
        self.logs_dir = logs_dir
        self.log_path = '%s/%s.log' % (self.logs_dir, self.log_name)

        # the following attributes should match YAML_ATTRS
        self.started = None
        self.stopped = None
        self.first_event = None
        self.last_event = None
        self.online = []
        self.times = []

    def read_log(self, prev_logs=()):
        if not self.peek_start():
            if len(prev_logs) > 0:
                prev_log = prev_logs[-1]
                prev_log.read_log(prev_logs[:-1])
                self.online = prev_log.online
                self.times = prev_log.times
            else:
                raise ValueError('First log and no server start')
        try:
            yaml_file = open(self.log_path + '.yaml', 'r')
        except PermissionError:
            # no converted file exists, create it
            self.convert_log()
        else:  # converted file exists, read it
            with yaml_file:
                data = yaml.load(yaml_file)
                for attr in YAML_ATTRS:
                    setattr(self, attr, data[attr])

    def convert_log(self):
        if self.log_name == 'latest':
            log_file = open(self.log_path, 'r')
        else:
            log_file = gzip.open(self.log_path + '.gz', 'rb')
        with log_file:
            for line in log_file:
                pass  # TODO hard work is done here

    def write_yaml(self):
        if self.log_name == 'latest':
            print('[write_yaml] not writing latest, aborting')
            return
        with open(self.log_path + '.yaml', 'w') as yaml_file:
            data = {}
            for attr in YAML_ATTRS:
                data[attr] = getattr(self, attr)
            yaml.dump(data, stream=yaml_file)

    def peek_start(self):
        if self.started is not None:
            # already peeked
            return self.started
        try:
            yaml_file = open(self.log_path + '.yaml', 'r')
        except PermissionError:
            # no converted file exists, peek log file
            if self.log_name == 'latest':
                log_file = open(self.log_path, 'r')
            else:
                log_file = gzip.open(self.log_path + '.gz', 'rb')
            with log_file:
                for line in log_file:
                    self.started = bool(RE_START.match(line))
                    return self.started
                self.started = False
                return self.started  # empty log
        else:  # converted file exists, peek it
            with yaml_file:
                for line in yaml_file:
                    if line[:9] == 'started: ':
                        self.started = line[9] in 'yt'  # yes or true
                        return self.started
                    break
                raise ValueError('YAML file does not start with `started: `')


class AllLogs:
    def __init__(self, logs_dir):
        self.logs_dir = logs_dir
        self.logs = {}
        self.sorted_split_log_names = self.collect_sorted_split_log_names()

    def collect_sorted_split_log_names(self):
        unsorted_paths = glob.iglob(self.logs_dir + '/*.log.gz')
        unsorted_log_names = map(lambda p: os.path.split(p)[1][:-7], unsorted_paths)
        sorted_split_log_names = sorted(map(lambda s: [int(i) for i in s.split('-')], unsorted_log_names))
        return sorted_split_log_names

    def read_interval(self, from_day, to_day):
        """
        from_day, to_day are in format yyyy-mm-dd
        """
        logs_before = self.get_log_names_between(self.sorted_split_log_names, None, to_day)
        for log_name in self.get_log_names_between(logs_before, from_day, to_day):
            self.logs[log_name] = LogFile(self.logs_dir, log_name)
            self.logs[log_name].read_log(self.get_log_names_between(logs_before, None, log_name))
            # TODO read_interval

    @staticmethod
    def get_log_names_between(sorted_split_log_names, from_log, to_log):
        """
        from_log, to_log are in format yyyy-mm-dd or yyyy-mm-dd-n,
        from_log may be None to accept all logs before to_log
        """
        if from_log is None:
            from_log = '0000-00-00'
        from_split = [int(i) for i in from_log.split('-')]
        to_split = [int(i) for i in to_log.split('-')]
        logs_in_range = filter(lambda log: from_split <= log < to_split, sorted_split_log_names)
        return map(lambda ii: '%i-%02i-%02i-%i' % ii, logs_in_range)


if __name__ == '__main__':
    f = AllLogs("../logs/")
    f.read_interval("2014-08-12", "2014-08-14")
