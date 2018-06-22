import unittest
import mock
from freezegun import freeze_time
import datetime
import json

from hubble import simulate_error


class SimulateErrorTestCase(unittest.TestCase):

    def setUp(self):
        return

    def tearDown(self):
        return

    def test_simulate_incoming_errors(self):
        return

    def test_simulate_process_errors(self):
        return

    def test_simulate_insight_lambda(self):
        # mock calls to child functions
        return

    def test_simulate_insight_gcp_lambda(self):
        raw_log = {
            'appId': 's~service',
            'endTime': '2018-06-14T12:00:00.000000Z',
            'latency': '',
            'resource': 'context@type',
            'stack': '',
            'versionId': ''
        }
        log = simulate_error.simulate_insight_gcp_lambda(raw_log, 'project')
        self.assertEqual({
            '_time': '2018-06-14T12:00:00.000000Z',
            'appId': 's~project',
            'latency': '',
            'resource': 'context@type',
            'stack': '',
            'versionId': ''
        }, log)
        raw_log = {
            'appId': 's~service',
            'endTime': '2018-06-14T12:00:00.000000Z',
            'latency': '',
            'resource': 'context@type',
            'stack': '',
            'versionId': ''
        }
        log = simulate_error.simulate_insight_gcp_lambda(raw_log, '')
        self.assertEqual({
            '_time': '2018-06-14T12:00:00.000000Z',
            'appId': 's~service',
            'latency': '',
            'resource': 'context@type',
            'stack': '',
            'versionId': ''
        }, log)

    @freeze_time("2018-06-14 12:00:00.000000")
    def test_simulate_insight_kinesis_lambda(self):
        raw_log = {
            'exception': {
              'stacktrace': '',
              'message': 'context@type',
              'type': ''
            },
            'service': {
                'name': 'service'
            },
            'level': '',
            'timestamp': '2018-06-14T12:00:00.000000Z',
            'context': {},
            'message': '',
            'metadata': {
              'logger': '',
              'app_version': ''
            }
        }
        log = simulate_error.simulate_insight_kinesis_lambda(
            raw_log, 'project', 'env')
        self.assertEqual({
            'exception': {
              'stacktrace': '',
              'message': 'context@type',
              'type': ''
            },
            'service': 'project-env',
            'level': '',
            'time': '2018/06/14 12:00:00',
            'context': {},
            'message': '',
            'metadata': {
              'logger': '',
              'app_version': ''
            }
        }, log)
        raw_log = {
            'exception': {
              'stacktrace': '',
              'message': 'context@type',
              'type': ''
            },
            'service': {
                'name': 'service'
            },
            'level': '',
            'timestamp': '2018-06-14T12:00:00.000000Z',
            'context': {},
            'message': '',
            'metadata': {
              'logger': '',
              'app_version': ''
            }
        }
        log = simulate_error.simulate_insight_kinesis_lambda(
            raw_log, '', '')
        self.assertEqual({
            'exception': {
              'stacktrace': '',
              'message': 'context@type',
              'type': ''
            },
            'service': 'service',
            'level': '',
            'time': '2018/06/14 12:00:00',
            'context': {},
            'message': '',
            'metadata': {
              'logger': '',
              'app_version': ''
            }
        }, log)
        raw_log = {
            'exception': {
              'stacktrace': '',
              'message': 'context@type',
              'type': ''
            },
            'service': {
                'name': 'app-int-collection-gateway'
            },
            'level': '',
            'timestamp': '2018-06-14T12:00:00.000000Z',
            'context': {},
            'message': '',
            'metadata': {
              'logger': '',
              'app_version': '',
              'app_name': 'service'
            }
        }
        log = simulate_error.simulate_insight_kinesis_lambda(
            raw_log, '', '')
        self.assertEqual({
            'exception': {
              'stacktrace': '',
              'message': 'context@type',
              'type': ''
            },
            'service': 'service',
            'source': 'client',
            'level': '',
            'time': '2018/06/14 12:00:00',
            'context': {},
            'message': '',
            'metadata': {
              'logger': '',
              'app_version': '',
              'app_name': 'service'
            }
        }, log)

    def test_generate_default_log(self):
        timestamp = datetime.datetime.now()
        log = simulate_error.populate_default_log(
            '', timestamp, 'service', False)
        self.assertEqual({}, log)
        return

    @freeze_time("2018-06-14 12:00:00.000000")
    def test_populate_default_gcp_log(self):
        default_log = {
            'appId': '',
            'endTime': '',
            'latency': '',
            'resource': '',
            'stack': '',
            'versionId': ''
        }
        timestamp = datetime.datetime.now()
        log = simulate_error.populate_default_gcp_log(
            default_log, timestamp, 'service')
        self.assertEqual({
            'appId': 's~service',
            'endTime': '2018-06-14T12:00:00.000000Z',
            'latency': '',
            'resource': 'context@type',
            'stack': '',
            'versionId': ''
        }, log)

    @freeze_time("2018-06-14 12:00:00.000000")
    def test_populate_default_kinesis_log(self):
        default_log = {
            'exception': {
                'stacktrace': '',
                'message': '',
                'type': ''
            },
            'service': {},
            'level': '',
            'timestamp': '',
            'context': {},
            'message': '',
            'metadata': {
                'logger': '',
                'app_version': ''
            }
        }
        timestamp = datetime.datetime.now()
        log = simulate_error.populate_default_kinesis_log(
            default_log, timestamp, 'service', False)
        self.assertEqual({
            'exception': {
                'stacktrace': '',
                'message': 'context@type',
                'type': ''
            },
            'service': {
                'name': 'service'
            },
            'level': '',
            'timestamp': '2018-06-14T12:00:00.000000Z',
            'context': {},
            'message': '',
            'metadata': {
                'logger': '',
                'app_version': ''
            }
        }, log)
        log = simulate_error.populate_default_kinesis_log(
            default_log, timestamp, 'service', True)
        self.assertEqual({
            'exception': {
                'stacktrace': '',
                'message': 'context@type',
                'type': ''
            },
            'service': {
                'name': 'app-int-collection-gateway'
            },
            'level': '',
            'timestamp': '2018-06-14T12:00:00.000000Z',
            'context': {},
            'message': '',
            'metadata': {
                'app_name': 'service',
                'logger': '',
                'app_version': ''
            }
        }, log)

    def test_create_url(self):
        base, path = 'http://example.com', '/api'
        url = simulate_error.create_url(base, path)
        self.assertEqual('http://example.com/api', url)
        base, path = 'http://example.com', '/api'
        params = {'a': 1, 'b': 2, 'c': 3}
        url = simulate_error.create_url(base, path, params)
        self.assertEqual('http://example.com/api?a=1&b=2&c=3', url)

    @mock.patch('hubble.constants.SERVICE_SUFFIX', ['-env'])
    def test_get_service_env(self):
        service, env = simulate_error.get_service_env('service-prod')
        self.assertEqual('service', service)
        self.assertEqual('prod', env)
        service, env = simulate_error.get_service_env('service')
        self.assertEqual('service', service)
        self.assertEqual('', env)

    def test_open_json_file(self):
        # test valid JSON
        read_data = json.dumps({'a': 1, 'b': 2, 'c': 3})
        mock_open = mock.mock_open(read_data=read_data)
        with mock.patch('__builtin__.open', mock_open):
            result = simulate_error.open_json_file('filename')
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, result)
        # test invalid JSON
        read_data = ''
        mock_open = mock.mock_open(read_data=read_data)
        with mock.patch("__builtin__.open", mock_open):
            with self.assertRaises(ValueError) as context:
                simulate_error.open_json_file('filename')
            self.assertEqual(
                'filename is not valid JSON.', str(context.exception))
        # test file does not exist
        with self.assertRaises(IOError) as context:
            simulate_error.open_json_file('null')
        self.assertEqual(
            'null does not exist.', str(context.exception))
