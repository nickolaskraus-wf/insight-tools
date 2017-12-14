#!/usr/bin/python

# import argparse
import base64
import datetime
import hashlib
import json
import sys
import time

import requests

from settings import INSIGHT_STAGING_BASE_URL, INCOMING_KINESIS_ERRORS_PATH, \
    LOCAL_COOKIE, STAGING_COOKIE, TIME_FORMAT_NO_MICRO_SEC, SERVICE_SUFFIX


def main():
    # TODO: Add command line argument parser
    # # configure command line argument parser
    # parser = argparse.ArgumentParser(
    #     description='Simulate a Kinesis error log on Insight.')
    # group = parser.add_mutually_exclusive_group()
    # # service to which the error is sent
    # parser.add_argument('service',
    #                     help='service to which the error is sent')
    # # number of errors to send to Insight
    # parser.add_argument('-n', '--number', type=int, default=1,
    #                     help='number of errors to send')
    # # specify if error should be new
    # parser.add_argument('--new', action='store_true',
    #                     help='send new error')
    # # specify if error should be sent to local or staging Insight instance
    # group.add_argument('-l', '--local', action='store_true',
    #                     help='send to local instance')
    # group.add_argument('-s', '--staging', action='store_true',
    #                     help='send to staging instance')

    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    if sys.argv[1] == '-l' or sys.argv[1] == '--local':
        base_url = 'http://localhost:8080'
    else:
        base_url = INSIGHT_STAGING_BASE_URL

    # service is used for the log
    service = sys.argv[2]
    # env is used for the process_errors request
    env = get_service_env(service)
    print service, env
    now = datetime.datetime.now()
    _time = now.strftime('%Y/%m/%d %H:%M:%S')
    hash = hashlib.sha256(str(now))
    context = str(datetime.datetime.now()) + '-' + str(hash.hexdigest())[0:7]

    # content of error log
    log = {
        "context": {},
        "exception": {},
        "level": "",
        "message": context,
        "metadata": {
            "logger": "w_comments"
        },
        "service": service,
        "time": _time,
        "version": ""
    }

    encoded_data = base64.b64encode(json.dumps(log))
    raw_body = {'data': [encoded_data]}
    encoded_body = json.dumps(raw_body)

    # form data for POST /tasks/process_errors
    utcnow = datetime.datetime.utcnow()
    start_time = utcnow - datetime.timedelta(seconds=60)
    end_time = utcnow + datetime.timedelta(seconds=60)
    form_data = {
        "start_time": start_time.strftime(TIME_FORMAT_NO_MICRO_SEC),
        "end_time": end_time.strftime(TIME_FORMAT_NO_MICRO_SEC),
        "env": env or None,
        "source": "kinesis",
        "should_check_lock": "True"
    }

    print end_time, start_time

    process_errors = create_url(base_url, '/tasks/process_errors')
    incoming_errors = create_url(base_url, INCOMING_KINESIS_ERRORS_PATH)

    headers = {
        'Content-Type': 'application/json'
    }

    form_headers = {
        'X-AppEngine-QueueName': 'yes'
    }

    cookie = {
        "dev_appserver_login": LOCAL_COOKIE,
        "SACSID": STAGING_COOKIE}

    # simulate kinesis error
    r = requests.post(incoming_errors, headers=headers, data=encoded_body,
                      cookies=cookie)

    if r.status_code != 200:
        print 'An error has occurred. Status code: ' + str(r.status_code)
        # TODO: Use BeautifulSoup to parse error response
        print r.text
        sys.exit(1)
    else:
        print 'Success! Status code: ' + str(r.status_code)

    time.sleep(1)

    # simulate process_errors
    r = requests.post(process_errors, headers=form_headers, data=form_data,
                      cookies=cookie)

    if r.status_code != 200:
        print 'An error has occurred. Status code: ' + str(r.status_code)
        # TODO: Use BeautifulSoup to parse error response
        print r.text
        sys.exit(1)
    else:
        print 'Success! Status code: ' + str(r.status_code)


def create_url(base, path, params=None):
    if not params:
        return base + path
    else:
        url = base + path + '?'
        for key, value in params.iteritems():
            url += key + '=' + str(value) + '&'
        return url


def get_service_env(service):
    """
    Get service env (Cerberus-prod => -prod).

    :param service: name of the service
    :type service: str
    :return: env
    :rtype: str
    """
    for suffix in SERVICE_SUFFIX:
        if suffix in service:
            return suffix
    return ''


def usage():
    print 'usage: simulate_new_gcp_error.py [-l | --local][-s | --staging] [project]'


if __name__ == '__main__':
    main()
