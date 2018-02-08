import base64

import requests

from settings import JIRA_USER, JIRA_PASS, JIRA_HOST


def jira_fetch(path):
    url = JIRA_HOST + path

    auth = base64.b64encode('%s:%s' % (JIRA_USER, JIRA_PASS))

    headers = {
        'Authorization': 'Basic %s' % auth,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    return response
