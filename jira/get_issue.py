"""
Description:
    Returns a full representation of the issue for the given issue key.

Usage:
  Options:

  Arguments
    issueIdOrKey    ID or key of the issue

Jira Cloud Rest API

GET /rest/api/2/issue/{issueIdOrKey}

Returns a full representation of the issue for the given issue key.

The issue JSON consists of the issue key and a collection of fields. Additional
information like links to workflow transition sub-resources, or HTML rendered
values of the fields supporting HTML rendering can be retrieved with expand re-
quest parameter specified.

The fields request parameter accepts a comma-separated list of fields to in-
clude in the response. It can be used to retrieve a subset of fields. By de-
fault all fields are returned in the response. A particular field can be ex-
cluded from the response if prefixed with a "-" (minus) sign. Parameter can be
provided multiple times on a single request.

By default, all fields are returned in the response. Note: this is different
from a JQL search - only navigable fields are returned by default (*navigable).

App scope required: READ
Response content type: application/json

"""
import json
import sys

from api import jira_fetch


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    issue = sys.argv[1]

    result = jira_fetch('/rest/api/2/issue/{}'.format(issue))

    print 'Status:'
    print result.status_code
    print 'Response:'
    try:
        parsed = json.loads(result.content)
        print json.dumps(parsed, indent=4, sort_keys=True)
    except ValueError as e:
        print 'Error: {}'.format(e)
        print result.text


def usage():
    print 'usage: get_issue_status.py <issue>'


if __name__ == '__main__':
    main()
