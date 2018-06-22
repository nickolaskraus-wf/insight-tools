"""
usage: simulate_error.py [-h] [-s] [-n | -r] [-t TIME] [-c COUNT] [-f FILE]
                         [-p PROJECT]
                         {gcp,kinesis}

Simulate error(s) from GCP or Kinesis.

positional arguments:
  {gcp,kinesis}         source from which the error(s) is sent

optional arguments:
  -h, --help            show this help message and exit
  -s, --staging         send to staging instance, defaults to local
  -n, --new             send new error(s)
  -r, --resurfaced      send resurfaced error(s)
  -t TIME, --time TIME  date and time of the error(s). Format: Y-m-d H:M:S
  -c COUNT, --count COUNT
                        number of errors to send
  -f FILE, --file FILE  file containing a log
  -p PROJECT, --project PROJECT
                        project from which the error(s) is sent
"""

import argparse
import base64
import copy
import datetime
import hashlib
import json
import sys
import time
import random

import requests

from constants import (BASE_URL_LOCAL, BASE_URL_STAGING, DEFAULT_GCP_FILE,
                       DEFAULT_KINESIS_FILE, INCOMING_GCP_ERRORS,
                       INCOMING_KINESIS_ERRORS, SERVICE_SUFFIX,
                       TIME_FORMAT_DEFAULT_DATETIME, TIME_FORMAT_GCP_RAW_ERROR,
                       TIME_FORMAT_KINESIS_ERROR, TIME_FORMAT_KINESIS_RAW_ERROR,
                       TIME_FORMAT_NO_MICRO_SEC)
from settings import (COOKIE_LOCAL, COOKIE_STAGING)


def parse_args():
    # configure command line argument parser
    parser = argparse.ArgumentParser(
        description='Simulate error(s) from GCP or Kinesis.')

    # specify if error(s) should be sent to staging, defaults to local
    parser.add_argument('-s', '--staging', action='store_true',
                        help='send to staging instance, defaults to local')

    group = parser.add_mutually_exclusive_group()

    # specify if error(s) should be new or resurfaced, defaults to
    # 'context@type'
    group.add_argument('-n', '--new', action='store_true',
                       help='send new error(s)')
    group.add_argument('-r', '--resurfaced', action='store_true',
                       help='send resurfaced error(s)')

    # specify the date and time of the error(s), defaults to
    # datetime.datetime.now()
    parser.add_argument('-t', '--time', default=None,
                        help='date and time of the error(s). Format: {}'.
                        format(TIME_FORMAT_DEFAULT_DATETIME.replace('%', '')))

    # specify the number of errors to send, defaults to 1
    parser.add_argument('-c', '--count', type=int, default=1,
                        help='number of errors to send')

    # specify the file containing the log for the error
    parser.add_argument('-f', '--file', default=None,
                        help='file containing a log')

    # project from which the error(s) is sent
    parser.add_argument('-p', '--project', default=None,
                        help='project from which the error(s) is sent')

    # source (gcp or kinesis) from which the error(s) is sent
    parser.add_argument('source', choices=['gcp', 'kinesis'],
                        help='source from which the error(s) is sent')

    return parser.parse_args()


def main():
    errors = []
    args = parse_args()

    if args.project:
        service, env = get_service_env(args.project)
    else:
        service, env = '', ''

    if args.staging:
        base_url = BASE_URL_STAGING
    else:
        base_url = BASE_URL_LOCAL

    if args.source == 'gcp':
        url = create_url(base_url, INCOMING_GCP_ERRORS)
    else:
        url = create_url(base_url, INCOMING_KINESIS_ERRORS)

    if args.time:
        try:
            time = datetime.datetime.strptime(
                args.time, TIME_FORMAT_DEFAULT_DATETIME)
        except ValueError:
            raise ValueError(
                'Argument -t TIME must be in the format: {}.'.format(
                    TIME_FORMAT_DEFAULT_DATETIME))
    else:
        time = datetime.datetime.now()

    if args.file:
        log = open_json_file(args.file)
    else:
        log = populate_default_log(args.source, time, service)

    log = simulate_insight_lambda(args.source, log, service, env)

    hash = hashlib.sha256(str(datetime.datetime.now()))

    if args.new:
        if args.source == 'gcp':
            log['resource'] += '{}{}'.format(
                '-', str(hash.hexdigest())[0:7])
        elif args.source == 'kinesis':
            log['exception']['message'] += '{}{}'.format(
                '-', str(hash.hexdigest())[0:7])
    elif args.resurfaced:
        # TODO: resurfaced errors currently do not work
        log_copy = copy.deepcopy(log)
        if args.source == 'gcp':
            log_copy['_time'] = time - datetime.timedelta(days=90)
        elif args.source == 'kinesis':
            log_copy['time'] = time - datetime.timedelta(days=90)
        errors.append(log_copy)

    for i in range(args.count):
        errors.append(copy.deepcopy(log))

    for e in errors:
        hash = hashlib.sha256(str(datetime.datetime.now()))
        stacktrace = e['exception']['stacktrace']
        e['exception']['stacktrace'] = stacktrace.replace(
            'x', str(hash.hexdigest())[0:7])

    simulate_incoming_errors(errors, url)

    if not args.staging:
        url = create_url(base_url, '/tasks/process_errors')
        simulate_process_errors(env, args.source, url)


def simulate_incoming_errors(errors, url):
    """
    Simulate incoming error(s) from GCP or Kinesis.

    Uses the Insight API to simulate incoming error:
        - /api/v1/hubble/incoming_gcp_errors
        - /api/v1/hubble/incoming_errors

    :param errors: list of dicts corresponding to errors
    :type errors: list
    :param url: url for incoming errors endpoint
    :type url: str
    :return: None
    :rtype: None
    """
    headers = {
        'Content-Type': 'application/json'
    }

    cookies = {
        'dev_appserver_login': COOKIE_LOCAL,
        'SACSID': COOKIE_STAGING
    }

    for e in errors:
        data = json.dumps({'data': [base64.b64encode(json.dumps(e))]})

        response = requests.post(
            url, headers=headers, data=data, cookies=cookies)

        if response.status_code == 200:
            continue
        elif response.status_code == 403:
            print 'Error! 403 Forbidden.'
            sys.exit(1)

    print 'Success!'
    time.sleep(1)


def simulate_process_errors(env, source, url):
    """
    Simulate process error(s).

    Uses the Insight API to simulate process error(s):
        - /cron/create_tasks_to_process_errors

    :param env: environment from which the error(s) is sent:
        prod, eu, demo, sandbox, wk-dev, or eu
    :type env: str
    :param source: source from which the error(s) is sent:
        gcp, kinesis
    :type source: str
    :param url: url for process errors endpoint
    :type url: str
    :return: None
    :rtype: None
    """
    utc = datetime.datetime.utcnow()
    start_time = utc - datetime.timedelta(seconds=60)
    end_time = utc + datetime.timedelta(seconds=60)
    form_data = {
        'start_time': start_time.strftime(TIME_FORMAT_NO_MICRO_SEC),
        'end_time': end_time.strftime(TIME_FORMAT_NO_MICRO_SEC),
        'env': env or None,
        'source': source,
        'should_check_lock': 'True'
    }

    headers = {
        'X-AppEngine-QueueName': 'yes'
    }

    cookies = {
        'dev_appserver_login': COOKIE_LOCAL,
        'SACSID': COOKIE_STAGING
    }

    response = requests.post(
        url, headers=headers, data=form_data, cookies=cookies)

    if response.status_code == 200:
        print 'Success!'
    elif response.status_code == 403:
        print 'Error! 403 Forbidden.'
        sys.exit(1)


def simulate_insight_lambda(source, log, service, env):
    """
    Process a raw GCP or Kinesis error log.

    :param source: source from which the error(s) is sent:
        gcp, kinesis
    :type source: str
    :param log: log to be processed
    :type log: dict
    :param service: service from which the error(s) is sent
    :type service: str
    :param env: environment from which the error(s) is sent:
        prod, eu, demo, sandbox, wk-dev, or eu
    :type env: str
    :return: processed log
    :rtype: dict
    """
    if source == 'gcp':
        return simulate_insight_gcp_lambda(log, service)
    elif source == 'kinesis':
        return simulate_insight_kinesis_lambda(log, service, env)


def simulate_insight_gcp_lambda(log, service):
    """
    Process a raw GCP error log.

    After processing, a log from GCP has the following form:
    {
      "_time": "%Y-%m-%dT%H:%M:%S.0000Z",
      "appId": "s~service",
      "latency": "",
      "resource": "",
      "stack": "",
      "versionId": ""
    }

    :param log: raw GCP error log
    :type log: dict
    :param service: service from which the error(s) is sent
    :type service: str
    :return: processed, GCP error log
    :rtype: dict
    """
    _time = log.get('endTime')
    app_id = log.get('appId')
    latency = log.get('latency')
    resource = log.get('resource')
    version_id = log.get('versionId')

    if service:
        app_id = '{}{}'.format('s~', service)

    error = {
        '_time': _time,
        'appId': app_id,
        'resource': resource,
        'latency': latency,
        'stack': '',
        'versionId': version_id,
    }

    return error


def simulate_insight_kinesis_lambda(log, service, env):
    """
    Process a raw Kinesis error log.

    After processing, a log from Kinesis has the following form:
    {
      "context": {},
      "exception": {},
      "level": "",
      "message": "",
      "metadata": {},
      "service": "service-env",
      "time": "%Y/%m/%d %H:%M:%S"
    }

    :param log: raw Kinesis error log
    :type log: dict
    :param service: service from which the error(s) is sent
    :type service: str
    :param env: environment from which the error(s) is sent:
        prod, eu, demo, sandbox, wk-dev, or eu
    :type env: str
    :return: processed, Kinesis error log
    :rtype: dict
    """
    context = log.get('context', {})
    exception = log.get('exception', {})
    level = log.get('level', 'info')
    message = log.get('message', '')
    metadata = log.get('metadata', {})
    version_name = log.get('container', {}).get('name')

    source = ''

    if service:
        service = service
    else:
        service = log.get('service', {}).get('name') or ''
        if 'app-int-collection-gateway' in service:
            service = metadata.get('app_name', service)
            source = 'client'

    if env:
        service = '{}-{}'.format(service, env)

    # timestamp is of form: %Y-%m-%dT%H:%M:%S.%fZ or %Y-%m-%dT%H:%M:%SZ
    timestamp = log.get('timestamp')
    if timestamp.find('.') >= 0:
        time = datetime.datetime.strptime(
            timestamp.rsplit('.', 1)[0], "%Y-%m-%dT%H:%M:%S")
    else:
        time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    if service:
        error = {
            'context': context,
            'exception': exception,
            'level': level,
            'message': message,
            'metadata': metadata,
            'service': service,
            'time': time.strftime(TIME_FORMAT_KINESIS_ERROR)
        }

        if source:
            error['source'] = source

        if version_name:
            error['version'] = version_name

        return error

    else:
        raise ValueError('Log does not contain a service.')


def populate_default_log(source, time, service, is_frontend=False):
    """
    Populate a default, raw error log using a given time and service.

    The source is used to determine the log format (gcp or kinesis).

    :param source: source from which the error(s) is sent:
        gcp, kinesis
    :type source: str
    :param time: timestamp of the log
    :type time: datetime.datetime
    :param service: service from which the error(s) is sent
    :type service: str
    :param is_frontend: if the log is from the frontend
    :type is_frontend: bool
    :return: default error log
    :rtype: dict
    """
    log = {}

    if source == 'gcp':
        filename = DEFAULT_GCP_FILE
    elif source == 'kinesis':
        filename = DEFAULT_KINESIS_FILE
    else:
        # if source is not gcp or kinesis, return empty log
        return log

    log = open_json_file(filename)

    if source == 'gcp':
        return populate_default_gcp_log(log, time, service)
    elif source == 'kinesis':
        return populate_default_kinesis_log(log, time, service, is_frontend)


def populate_default_gcp_log(log, timestamp, service):
    """
    Populate a default, raw GCP error log using a given time and service.

    A log from GCP has the following form:
    {
      "appId": "s~service",
      "endTime": "%Y-%m-%dT%H:%M:%S.%fZ",
      "latency": "",
      "resource": "",
      "stack": "",
      "versionId": ""
    }

    :param log: default, Kinesis error log
    :type log: dict
    :param timestamp: timestamp of the log
    :type timestamp: datetime.datetime
    :param service: service from which the error(s) is sent
    :type service: str
    :return:
    """
    log['appId'] = '{}{}'.format('s~', service)
    log['endTime'] = datetime.datetime.strftime(
        timestamp, TIME_FORMAT_GCP_RAW_ERROR)
    log['resource'] = 'context@type'
    return log


def populate_default_kinesis_log(log, timestamp, service, is_frontend=False):
    """
    Populate a default, raw Kinesis error log using a given time and service.

    A log from Kinesis has the following form:
    {
      "context": {},
      "exception": {},
      "level": "",
      "message": "",
      "metadata": {},
      "service": {
        "name": "service"
      }
      "timestamp": "%Y-%m-%dT%H:%M:%S.%fZ" | "%Y-%m-%dT%H:%M:%SZ"
    }

    A log from Kinesis frontend has the following form:
    {
      "context": {},
      "exception": {},
      "level": "",
      "message": "",
      "metadata": {
        "app_name": "service"
      },
      "service": {
        "name": "app-int-collection-gateway"
      }
      "timestamp": "%Y-%m-%dT%H:%M:%S.%fZ"
    }

    If service:name is 'app-int-collection-gateway', metadata:app_name is used.
    These logs are generated by App Intelligence.

    :param log: default, Kinesis error log
    :type log: dict
    :param timestamp: timestamp of the log
    :type timestamp: datetime.datetime
    :param service: service from which the error(s) is sent
    :type service: str
    :param is_frontend: if the log is from the frontend
    :type is_frontend: bool
    :return:
    """
    log['exception']['message'] = 'context@type'
    log['timestamp'] = datetime.datetime.strftime(
        timestamp, TIME_FORMAT_KINESIS_RAW_ERROR)
    if not is_frontend:
        log['service'] = {
            'name': service
        }
    else:
        log['metadata']['app_name'] = service
        log['service'] = {
            'name': 'app-int-collection-gateway'
        }
    return log


def create_url(base, path, params=None):
    """
    Create a valid URL using base, path, and parameters.

    :param base: protocol, domain, and port
    :type base: str
    :param path: path to resource
    :type path: str
    :param params: optional parameters
    :type params: dict
    :return: url
    :rtype: str
    """
    if not params:
        return base + path
    else:
        url = base + path + '?'
        for key, value in sorted(params.iteritems()):
            url += key + '=' + str(value) + '&'
        return url[:-1]


def get_service_env(service):
    """
    Return the service and environment.

    Example:
        Cerberus-prod => 'Cerberus' 'prod'

    Service environment can be:
        prod, eu, demo, sandbox, wk-dev, or eu

    If the service does not have an environment appended onto its name, an em-
    pty string is returned.

    :param service: name of the service with environment
    :type service: str
    :return: service, environment (prod, eu, demo, sandbox, wk-dev, or eu)
    :rtype: str, str
    """
    for suffix in SERVICE_SUFFIX:
        if suffix in service:
            return service.rsplit(suffix, 1)[0], suffix[1:]
    return service, ''


def open_json_file(filename):
    """
    Attempt to open and deserialize a JSON file.

    :param filename: name of the JSON file
    :type filename: str
    :return: dict of log
    :rtype: dict
    """
    try:
        with open(filename) as f:
            try:
                return json.load(f)
            except ValueError:
                raise ValueError('{} is not valid JSON.'.format(filename))
    except IOError:
        raise IOError('{} does not exist.'.format(filename))


if __name__ == '__main__':
    main()
