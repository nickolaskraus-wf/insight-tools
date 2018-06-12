"""
usage: simulate_error.py [-h] [-l | -s] [-n | -r] [-t TIME] [-c COUNT]
                         [-f FILE]
                         {gcp,kinesis} service

Simulate error(s) from GCP or Kinesis.

positional arguments:
  {gcp,kinesis}         source from which the error(s) is sent
  service               service to which the error(s) is sent

optional arguments:
  -h, --help            show this help message and exit
  -l, --local           send to local instance
  -s, --staging         send to staging instance
  -n, --new             send new error(s)
  -r, --resurfaced      send resurfaced error(s)
  -t TIME, --time TIME  date and time of the error(s). Format: Y-m-d H:M:S
  -c COUNT, --count COUNT
                        number of errors to send
  -f FILE, --file FILE  file containing a log
"""

import argparse
import base64
import copy
import datetime
import hashlib
import json
import sys
import time

import requests

from constants import (BASE_URL_LOCAL, BASE_URL_STAGING, SERVICE_SUFFIX,
                       TIME_FORMAT_DEFAULT_DATETIME, TIME_FORMAT_NO_MICRO_SEC,
                       TIME_FORMAT_GCP_ERROR, TIME_FORMAT_KINESIS_ERROR)
from settings import (COOKIE_LOCAL, COOKIE_STAGING)


def parse_args():
    # configure command line argument parser
    parser = argparse.ArgumentParser(
        description='Simulate error(s) from GCP or Kinesis.')

    group = parser.add_mutually_exclusive_group()

    # specify if error(s) should be sent to a local or staging instance, de-
    # faults to 'local'
    group.add_argument('-l', '--local', action='store_true',
                       help='send to local instance')
    group.add_argument('-s', '--staging', action='store_true',
                       help='send to staging instance')

    group = parser.add_mutually_exclusive_group()

    # specify if error(s) should be new or resurfaced, defaults to
    # 'context@type'
    group.add_argument('-n', '--new', action='store_true',
                       help='send new error(s)')
    group.add_argument('-r', '--resurfaced', action='store_true',
                       help='send resurfaced error(s)')

    # specify the date and time of the error(s)
    parser.add_argument('-t', '--time', default=datetime.datetime.now(),
                        help='date and time of the error(s). Format: {}'.
                        format(TIME_FORMAT_DEFAULT_DATETIME.replace('%', '')))

    # specify the number of errors to send, defaults to 1
    parser.add_argument('-c', '--count', type=int, default=1,
                        help='number of errors to send')

    # specify the file containing the log for the error
    parser.add_argument('-f', '--file', default=None,
                        help='file containing a log')

    # source (gcp or kinesis) from which the error(s) is sent
    parser.add_argument('source', choices=['gcp', 'kinesis'],
                        help='source from which the error(s) is sent')

    # service from which the error(s) is sent
    parser.add_argument('service',
                        help='service from which the error(s) is sent')

    return parser.parse_args()


def main():
    errors = []
    args = parse_args()

    if args.local:
        base_url = BASE_URL_LOCAL
    elif args.staging:
        base_url = BASE_URL_STAGING
    else:
        base_url = BASE_URL_LOCAL

    url = ''
    if args.source == 'gcp':
        url = create_url(base_url, '/api/v1/hubble/incoming_gcp_errors')
    elif args.source == 'kinesis':
        url = create_url(base_url, '/api/v1/hubble/incoming_errors')

    service, env = get_service_env(args.service)

    if isinstance(args.time, str):
        try:
            time = datetime.datetime.strptime(
                args.time, TIME_FORMAT_DEFAULT_DATETIME)
        except ValueError:
            raise ValueError(
                'Argument -t, --time must be in the format: {}'.format(
                    TIME_FORMAT_DEFAULT_DATETIME))
    else:
        time = args.time

    hash = hashlib.sha256(str(datetime.datetime.now()))

    log = {}
    if args.file:
        try:
            with open(args.file) as f:
                try:
                    log = json.load(f)
                    log = simulate_insight_lambda(log)
                except ValueError:
                    raise ValueError('{} is not valid JSON'.format(args.file))
        except IOError:
            raise IOError('{} does not exist'.format(args.file))
    else:
        log = generate_default_log(time, args.source, args.service)

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

    errors = [log] * args.count

    simulate_incoming_errors(errors, url)

    if args.local:
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
    :return:
    :rtype:
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

        r = requests.post(url, headers=headers, data=data, cookies=cookies)

        if r.status_code != 200:
            print 'An error has occurred. Status code: ' + str(r.status_code)
            # TODO: Use BeautifulSoup to parse error response
            print r.text
            sys.exit(1)
        else:
            print 'Success! Status code: ' + str(r.status_code)

    time.sleep(1)
    return


def simulate_process_errors(env, source, url):
    """
    Simulate process error(s).

    Uses the Insight API to simulate process error(s):
        - /cron/create_tasks_to_process_errors

    :param env: environment from which the error(s) is sent:
        prod, -eu, -demo, -sandbox, -wk-dev, or -eu
    :type env: str
    :param source: source from which the error(s) is sent:
        gcp, kinesis
    :type source: str
    :param url: url for process errors endpoint
    :type url: str
    :return:
    :rtype:
    """
    headers = {
        'X-AppEngine-QueueName': 'yes'
    }

    cookies = {
        'dev_appserver_login': COOKIE_LOCAL,
        'SACSID': COOKIE_STAGING
    }

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

    r = requests.post(url, headers=headers, data=form_data,
                      cookies=cookies)

    if r.status_code != 200:
        print 'An error has occurred. Status code: ' + str(r.status_code)
        # TODO: Use BeautifulSoup to parse error response
        print r.text
        sys.exit(1)
    else:
        print 'Success! Status code: ' + str(r.status_code)


def simulate_insight_lambda(log):
    """
    Simulate the Insight AWS Lambda function.

    :param log: log to be processed
    :type log: dict
    :return: processed log
    :rtype: dict
    """
    t = log.get('timestamp')
    if t.find('.') >= 0:
        timestamp = datetime.datetime.strptime(
            t.rsplit('.', 1)[0], "%Y-%m-%dT%H:%M:%S")
    else:
        timestamp = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

    log['time'] = timestamp.strftime('%Y/%m/%d %H:%M:%S')
    del log['timestamp']

    return log


def generate_default_log(time, source, service):
    """
    Generate a default error log using a given time, source, and service.

    :param time: timestamp of the log
    :type time: datetime.datetime
    :param source: source from which the error(s) is sent:
        gcp, kinesis
    :type source: str
    :param service: service from which the error(s) is sent
    :type service: str
    :return: default error log
    :rtype: dict
    """
    log = {}

    filename = ''
    if source == 'gcp':
        filename = 'logs/default_gcp.json'
    elif source == 'kinesis':
        filename = 'logs/default_kinesis.json'

    with open(filename) as f:
        try:
            log = json.load(f)
        except ValueError:
            raise ValueError('{} is not valid JSON'.format(filename))

    if source == 'gcp':
        log['_time'] = datetime.datetime.strftime(
            time, TIME_FORMAT_GCP_ERROR)
        log['appId'] = '{}{}'.format('s~', service)
        log['resource'] = 'context@type'
    elif source == 'kinesis':
        log['exception']['message'] = 'context@type'
        log['service'] = service
        log['time'] = datetime.datetime.strftime(
            time, TIME_FORMAT_KINESIS_ERROR)
    else:
        return {}

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
        for key, value in params.iteritems():
            url += key + '=' + str(value) + '&'
        return url


def get_service_env(service):
    """
    Return the service and environment.

    Example:
        Cerberus-prod => 'Cerberus' 'prod'

    Service environment can be:
        prod, -eu, -demo, -sandbox, -wk-dev, or -eu

    If the service does not have an environment appended onto its name, an em-
    pty string is returned.

    :param service: name of the service with environment
    :type service: str
    :return: service, environment (prod, eu, demo, sandbox, wk-dev, or eu)
    :rtype: str, str
    """
    for suffix in SERVICE_SUFFIX:
        if suffix in service:
            return service.rsplit(suffix, 1)[0], suffix
    return service, ''


if __name__ == '__main__':
    main()
