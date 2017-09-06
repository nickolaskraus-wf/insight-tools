#!/usr/bin/python

import base64
import datetime
import hashlib
import json
import sys
import time

import requests

from settings import INCOMING_GCP_ERRORS_PATH, LOCAL_COOKIE, PROCESS_ERRORS_PATH


def main():
    base_url = 'http://localhost:8080'

    url = create_url(base_url, INCOMING_GCP_ERRORS_PATH)

    headers = {
        'Content-Type': 'application/json',
    }

    cookie = {
        "dev_appserver_login": LOCAL_COOKIE
    }

    # kick off process errors if local
    r = requests.get(base_url + PROCESS_ERRORS_PATH, cookies=cookie)
    time.sleep(10)

    if r.status_code != 200:
        print 'An error has occurred. Status code: ' + str(r.status_code)
        sys.exit(1)
    else:
        print 'Success! Status code: ' + str(r.status_code)

    # simulate gcp error
    for i in range(0, 100000):

        now = str(datetime.datetime.now())
        hash = hashlib.sha256(str(now))

        resource = now + '-' + str(hash.hexdigest())[0:7]
        _time = str(now).replace(' ', 'T') + 'Z'
        project = 's~' + 'new-project' + str(hash.hexdigest())[0:7]

        log = {
            "latency": "0.01337s",
            "resource": resource,
            "_time": _time,
            "versionId": "xx.xx.xx",
            "appId": project,
            "stack": ""
        }

        encoded_data = base64.b64encode(json.dumps(log))
        raw_body = {'data': [encoded_data]}
        encoded_body = json.dumps(raw_body)

        r = requests.post(url, headers=headers, data=encoded_body,
                          cookies=cookie)

        if r.status_code != 200:
            print 'An error has occurred. Status code: ' + str(r.status_code)
            sys.exit(1)
        else:
            print 'Success! Status code: ' + str(r.status_code)

        time.sleep(1.0 / 1000.0)


def create_url(base, path, params=None):
    if not params:
        return base + path
    else:
        url = base + path + '?'
        for key, value in params.iteritems():
            url += key + '=' + str(value) + '&'
        return url


def usage():
    print 'usage: kill_insight.py'


if __name__ == '__main__':
    main()
