"""
Description:
    Returns the metadata for creating issues.

Usage:
  Options:
    -s, --show-fields      show fields in the createmeta response
    -r, --required-only    show only required fields in the createmeta response
  Arguments
    issuetypeIds      issue type IDs
    issuetypeNames    issue type names
    projectIds        project IDs
    projectKeys       project keys

Jira Cloud Rest API

GET /rest/api/2/issue/createmeta

Returns the metadata for creating issues. This includes the available projects,
issue types, fields (with information whether those fields are required) and
field types. Projects, in which the user does not have permission to create is-
sues, will not be returned.

The fields in the createmeta response correspond to the fields on the issue's
Create screen for the specific project/issuetype. Fields hidden from the screen
will not be returned in the createmeta response. Fields will only be returned
if expand=projects.issuetypes.fields is set. The results can be filtered by
project and/or issue type, controlled by the query parameters.

App scope required: READ
Response content type: application/json

"""
import base64
import json
import sys

import requests

from settings import JIRA_USER, JIRA_PASS, JIRA_HOST


def main():
    options = {}

    for arg in sys.argv:
        if arg == ('-s' or '--show-fields'):
            options['show_fields'] = True
        if arg == ('-r' or '--required-only'):
            options['required_only'] = True

    if len(sys.argv) > 3:
        if (len(sys.argv) - len(options)) % 2 != 1:
            print('Error: Incorrect number of command line arguments.')
            usage()
            sys.exit(1)

    arguments = sys.argv[len(options) + 1:]

    query = build_query(arguments, options.get('show_fields'))

    response = jira_fetch('/rest/api/2/issue/createmeta?{}'.format(query))

    print 'Status:'
    print response.status_code
    print 'Response:'
    try:
        parsed_reponse = parse_response(response.content,
                                        options.get('required_only'))
        print json.dumps(parsed_reponse, indent=4, sort_keys=True)
    except ValueError as e:
        print 'Error: {}'.format(e)
        print response.text


def build_query(arguments, show_fields):
    types = []
    parameters = []

    for x in range(0, len(arguments), 2):
        types.append(arguments[x])
        parameters.append(arguments[x + 1])

    if show_fields:
        query = 'expand=projects.issuetypes.fields&'
    else:
        query = ''

    for x in range(0, len(arguments) / 2):
        query += '{}={}{}'.format(types[x], parameters[x], '&')

    query = query[:-1]
    print 'Query: ' + '/rest/api/2/issue/createmeta?{}'.format(query)
    return query


def parse_response(response, required_only):
    parsed_response = json.loads(response)
    if required_only:
        try:
            fields = parsed_response['projects'][0]['issuetypes'][0]['fields']
            for field in fields.keys():
                if not fields[field]['required']:
                    del fields[field]
        except (IndexError, KeyError) as e:
            print 'Failed to parse response. Error: {}'.format(e)

    return parsed_response


def jira_fetch(path):
    url = JIRA_HOST + path

    auth = base64.b64encode('%s:%s' % (JIRA_USER, JIRA_PASS))

    headers = {
        'Authorization': 'Basic %s' % auth,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    return response


def usage():
    print 'usage: get_create_issue_meta.py [-s, --show-fields] ' \
          '[-r, --required-only] <query-type> <parameters> ...'


if __name__ == '__main__':
    main()
