import glob
import os
import unittest
import yaml
import logalyzer
import timeutils

UUID_HHL = '808e727f-895a-4ac2-b246-4b6da2ca9451'
UUID_ULEXOS = 'a1d94087-e9c0-412f-b90f-cff2c224d44f'
UUID_OFFLINEGOTT = '9f352de0-b533-425c-9435-89b918ae4602'

class TestUtils(unittest.TestCase):

    def test_date_str_to_epoch(self):
        self.assertEqual(1426114800, timeutils.date_str_to_epoch('2015-03-12'))
        self.assertEqual(1426114800, timeutils.date_str_to_epoch('2015-03-12 00:00:00'))
        self.assertEqual(1426114800, timeutils.date_str_to_epoch('2015-03-12', '00:00:00'))
        self.assertEqual(1426119001, timeutils.date_str_to_epoch('2015-03-12 01:10:01'))

    def test_epoch_to_date_str(self):
        self.assertEqual('2015-03-12 00:00:00', timeutils.epoch_to_date_str(1426114800))
        self.assertEqual('2015-03-12 00:00:09', timeutils.epoch_to_date_str(1426114809))
        self.assertEqual('2015-03-12 01:10:01', timeutils.epoch_to_date_str(1426119001))

    def test_ensure_full_date(self):
        self.assertEqual('2015-03-12 00:00:00', timeutils.ensure_full_date('2015-03-12'))
        self.assertEqual('2015-03-12 00:00:00', timeutils.ensure_full_date('2015-03-12 00:00:00'))
        self.assertEqual('2015-03-12 12:34:56', timeutils.ensure_full_date('2015-03-12 12:34:56'))

    def test_add_to_date_str(self):
        self.assertEqual('2015-03-12 00:00:00', timeutils.add_to_date_str('2015-03-12'))
        self.assertEqual('2015-03-11 00:00:00', timeutils.add_to_date_str('2015-03-12', days=-1))
        self.assertEqual('2015-03-14 01:02:03', timeutils.add_to_date_str('2015-03-12 05:02:03', days=2, hours=-4))


class TestYaml(unittest.TestCase):

    def test_compare_yaml(self):
        self.maxDiff = None
        count = 0
        for expected_path in glob.iglob('test_logs/*.expected.yaml'):
            with open(expected_path, 'r') as expected_file:
                expected_data = yaml.load(expected_file)
            log_path = expected_path.replace('expected', 'log')
            with open(log_path, 'r') as log_file:
                real_data = yaml.load(log_file)
            log_name = os.path.split(log_path)[1]
            self.assertDictEqual(expected_data, real_data, log_name)
            count += 1
        self.assertEqual(4, count, 'Not all .expected.yaml were read')


class TestSessions(unittest.TestCase):

    def setUp(self):
        self.test_logs = logalyzer.LogDirectory('test_logs/')
        self.assertEqual(5, len(self.test_logs.log_files), 'Not all log files recognized')
        self.maxDiff = None

    def tearDown(self):
        for log_file in self.test_logs.log_files.values():
            if log_file.been_read:
                break
        else:
            self.fail('No logs read')

    def test_coll_data_01_1(self):
        expected_online = {'HHL': [UUID_HHL, 1420084800, 1],
                           'Offlinegott': [UUID_OFFLINEGOTT, 1420095600, 1],
                           'Ulexos': [UUID_ULEXOS, 1420092000, 1], }
        expected_times = [[UUID_HHL, 1420077600, 1420081200, 'HHL']]

        times, online = self.test_logs.collect_data(None, '2015-01-02')
        self.assertDictEqual(expected_online, online, 'until midnight')
        self.assertListEqual(expected_times, times, 'until midnight')

        times, online = self.test_logs.collect_data(None, '2015-01-01 23:58:20')
        self.assertDictEqual(expected_online, online, 'before midnight')
        self.assertListEqual(expected_times, times, 'before midnight')

    def test_coll_sessions_01_1(self):
        user_sessions = self.test_logs.collect_user_sessions(None, '2015-01-02')
        self.assertDictEqual({
            UUID_HHL: [
                [UUID_HHL, 1420077600, 1420081200, 'HHL'],
                [UUID_HHL, 1420084800, 1420153200, 'HHL'],
            ], UUID_OFFLINEGOTT: [
                [UUID_OFFLINEGOTT, 1420095600, 1420153200, 'Offlinegott']
            ], UUID_ULEXOS: [
                [UUID_ULEXOS, 1420092000, 1420153200, 'Ulexos'],
            ]
        }, user_sessions, 'until midnight')

        user_sessions = self.test_logs.collect_user_sessions(None, '2015-01-01 23:58:20')
        self.assertDictEqual({
            UUID_HHL: [
                [UUID_HHL, 1420077600, 1420081200, 'HHL'],
                [UUID_HHL, 1420084800, 1420153100, 'HHL'],
            ], UUID_OFFLINEGOTT: [
                [UUID_OFFLINEGOTT, 1420095600, 1420153100, 'Offlinegott']
            ], UUID_ULEXOS: [
                [UUID_ULEXOS, 1420092000, 1420153100, 'Ulexos'],
            ]
        }, user_sessions, 'before midnight')

    def test_coll_data_02_1(self):
        expected_online = {'Offlinegott': [UUID_OFFLINEGOTT, 1420095600, 1],
                           'Ulexos': [UUID_ULEXOS, 1420171200, 1], }
        expected_times = [[UUID_HHL, 1420077600, 1420081200, 'HHL'],
                          [UUID_HHL, 1420084800, 1420167600, 'HHL'],
                          [UUID_ULEXOS, 1420092000, 1420171200, 'Ulexos']]

        times, online = self.test_logs.collect_data(None, '2015-01-03')
        self.assertDictEqual(expected_online, online, 'until midnight')
        self.assertListEqual(expected_times, times, 'until midnight')

        times, online = self.test_logs.collect_data(None, '2015-01-02 23:58:20')
        self.assertDictEqual(expected_online, online, 'before midnight')
        self.assertListEqual(expected_times, times, 'before midnight')

    def test_coll_sessions_02_1(self):
        user_sessions = self.test_logs.collect_user_sessions(None, '2015-01-03')
        self.assertDictEqual({
            UUID_HHL: [
                [UUID_HHL, 1420077600, 1420081200, 'HHL'],
                [UUID_HHL, 1420084800, 1420167600, 'HHL']
            ], UUID_ULEXOS: [
                [UUID_ULEXOS, 1420092000, 1420171200, 'Ulexos'],
                [UUID_ULEXOS, 1420171200, 1420239600, 'Ulexos']
            ], UUID_OFFLINEGOTT: [
                [UUID_OFFLINEGOTT, 1420095600, 1420239600, 'Offlinegott']
            ]
        }, user_sessions, 'until midnight')

        user_sessions = self.test_logs.collect_user_sessions(None, '2015-01-02 23:58:20')
        self.assertDictEqual({
            UUID_HHL: [
                [UUID_HHL, 1420077600, 1420081200, 'HHL'],
                [UUID_HHL, 1420084800, 1420167600, 'HHL']
            ], UUID_ULEXOS: [
                [UUID_ULEXOS, 1420092000, 1420171200, 'Ulexos'],
                [UUID_ULEXOS, 1420171200, 1420239500, 'Ulexos']
            ], UUID_OFFLINEGOTT: [
                [UUID_OFFLINEGOTT, 1420095600, 1420239500, 'Offlinegott']
            ]
        }, user_sessions, 'before midnight')

    def test_coll_data_04_1(self):
        expected_times = [[UUID_HHL, 1420077600, 1420081200, 'HHL'],
                          [UUID_HHL, 1420084800, 1420167600, 'HHL'],
                          [UUID_ULEXOS, 1420092000, 1420171200, 'Ulexos'],
                          [UUID_OFFLINEGOTT, 1420095600, 1420340400, 'Offlinegott'],
                          [UUID_ULEXOS, 1420171200, 1420340400, 'Ulexos'],
                          [UUID_HHL, 1420365600, 1420372800, 'HHL'],
                          [UUID_ULEXOS, 1420369200, 1420376400, 'Ulexos']]
        times, online = self.test_logs.collect_data(None, '2015-01-04 05:00:00')
        self.assertListEqual(expected_times, times)
        self.assertDictEqual({}, online)

        times, online = self.test_logs.collect_data(None, '2015-01-04 09:00:00')
        self.assertListEqual(expected_times, times)
        self.assertDictEqual({}, online)

    def test_coll_sessions_04_1(self):
        user_sessions = self.test_logs.collect_user_sessions(None, '2015-01-04 05:00:00')
        self.assertDictEqual({
            UUID_OFFLINEGOTT: [
                [UUID_OFFLINEGOTT, 1420095600, 1420340400, 'Offlinegott']
            ], UUID_HHL: [
                [UUID_HHL, 1420077600, 1420081200, 'HHL'],
                [UUID_HHL, 1420084800, 1420167600, 'HHL']
            ], UUID_ULEXOS: [
                [UUID_ULEXOS, 1420092000, 1420171200, 'Ulexos'],
                [UUID_ULEXOS, 1420171200, 1420340400, 'Ulexos']
            ]
        }, user_sessions, 'until midnight')

    def test_coll_data_04_2(self):
        times, online = self.test_logs.collect_data('2015-01-04 10:00:00', '2015-01-04 14:00:00')
        self.assertListEqual([[UUID_OFFLINEGOTT, 1420095600, 1420340400, 'Offlinegott'],
                              [UUID_ULEXOS, 1420171200, 1420340400, 'Ulexos'],
                              [UUID_HHL, 1420365600, 1420372800, 'HHL'],
                              [UUID_ULEXOS, 1420369200, 1420376400, 'Ulexos']], times)
        self.assertDictEqual({}, online)

        times, online = self.test_logs.collect_data('2015-01-04 09:00:00', '2015-01-04 15:00:00')
        self.assertListEqual([[UUID_OFFLINEGOTT, 1420095600, 1420340400, 'Offlinegott'],
                              [UUID_ULEXOS, 1420171200, 1420340400, 'Ulexos'],
                              [UUID_HHL, 1420365600, 1420372800, 'HHL'],
                              [UUID_ULEXOS, 1420369200, 1420376400, 'Ulexos']], times)
        self.assertDictEqual({}, online)

    def test_coll_sessions_04_2(self):
        user_sessions = self.test_logs.collect_user_sessions(None, '2015-01-05')
        return  # TODO
        self.assertDictEqual({}, user_sessions)

    def test_coll_data_latest(self):
        times, online = self.test_logs.collect_data(None, '2015-01-04 05:00:00')
        self.assertListEqual([[UUID_HHL, 1420077600, 1420081200, 'HHL'],
                              [UUID_HHL, 1420084800, 1420167600, 'HHL'],
                              [UUID_ULEXOS, 1420092000, 1420171200, 'Ulexos'],
                              [UUID_OFFLINEGOTT, 1420095600, 1420340400, 'Offlinegott'],
                              [UUID_ULEXOS, 1420171200, 1420340400, 'Ulexos'],
                              [UUID_HHL, 1420365600, 1420372800, 'HHL'],
                              [UUID_ULEXOS, 1420369200, 1420376400, 'Ulexos']], times)
        return  # TODO
        self.assertDictEqual({}, online)

        times, online = self.test_logs.collect_data(None, '2015-01-04 09:00:00')
        self.assertListEqual([], times)
        self.assertDictEqual({}, online)

    def test_coll_sessions_latest(self):
        user_sessions = self.test_logs.collect_user_sessions(None, '2015-01-04 05:00:00')
        return  # TODO
        self.assertDictEqual({}, user_sessions)


if __name__ == '__main__':
    unittest.main()
