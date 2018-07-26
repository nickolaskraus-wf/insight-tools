import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (BASE_URL_STAGING, START_RUNNING_APOLLO)
from settings import (COOKIE_LOCAL, COOKIE_STAGING)

# log_source_key for testing-in-3285.yaml
LOG_SOURCE_KEY = 'ahNzfnctaW5zaWdodC1zdGFnaW5nckoLEg9BcG9sbG9Mb2dTb3VyY2UiNW' \
                 'tpbmVzaXM6eydxdWVyeV9wYXJhbXMnOiB7J3R5cGUnOiAndW5rbm93bid9' \
                 'fTp3ay1kZXY6DA'


def main():
    simulate_start_running_apollo()
    return


def simulate_start_running_apollo():
    """
    Uses the Insight API to start Apollo in a Task Queue

    API Endpoint:
      - /tasks/start_running_apollo

    Request Form data:
      key                                                                  type
      log_source_key:
        URL safe key for the log source to start                           str
      start_time:
        time (Unix) the log source should start running                    str
      runner_id:
        unique ID for an ApolloTestRunner (if any)                         str
      force_start:
        force starts Apollo, ignores 'should_stop'                         str
      time_window:
        optional, time window to look for logs, defaults to 60.0 s         str

    :return: None
    :rtype: None
    """
    form_data = {
        'log_source_key': LOG_SOURCE_KEY,
        'start_time': time.time(),
        'runner_id': None,
        'force_start': 'true',
        'time_window': '60.0',
    }

    headers = {
        'X-AppEngine-QueueName': 'yes'
    }

    cookies = {
        'dev_appserver_login': COOKIE_LOCAL,
        'SACSID': COOKIE_STAGING
    }

    url = create_url(BASE_URL_STAGING, START_RUNNING_APOLLO)

    response = requests.post(
        url, headers=headers, data=form_data, cookies=cookies)

    if response.status_code == 200:
        print 'Success!'
    elif response.status_code == 403:
        print 'Error! 403 Forbidden.'
        sys.exit(1)
    else:
        print 'Error! {}'.format(response.status_code)
        sys.exit(1)


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


if __name__ == '__main__':
    main()
