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
import json
import sys

from api import jira_fetch


def main():
    options = {}

    for arg in sys.argv:
        if arg in ('-s', '--show-fields'):
            options['show_fields'] = True
        if arg in ('-r', '--required-only'):
            options['required_only'] = True

    if len(sys.argv) > len(options):
        if (len(sys.argv) - len(options)) % 2 != 1:
            print('Error: Incorrect number of command line arguments.')
            usage()
            sys.exit(1)

    arguments = sys.argv[len(options) + 1:]

    url = build_url('/rest/api/2/issue/createmeta', arguments,
                    options.get('show_fields'))

    response = jira_fetch(url)

    print 'Status:'
    print response.status_code
    print 'Response:'
    try:
        parsed_reponse = parse_response(response.content,
                                        options.get('required_only'))
        print json.dumps(parsed_reponse, indent=4, sort_keys=True)
    except ValueError as e:
        print 'Error: {}'.format(e)


def build_url(path, arguments, show_fields):
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
    url = '{}?{}'.format(path, query)
    print 'URL: ' + url
    return url


def parse_response(response, required_only):
    parsed_response = json.loads(response)
    if required_only:
        try:
            projects = parsed_response['projects']
            for project in projects:
                issuetypes = project['issuetypes']
                for issuetype in issuetypes:
                    fields = issuetype['fields']
                    for field in fields.keys():
                        if not fields[field]['required']:
                            del fields[field]
        except (IndexError, KeyError) as e:
            print 'Failed to parse response. Error: {}'.format(e)

    return parsed_response


def usage():
    print 'usage: get_create_issue_meta.py [-s, --show-fields] ' \
          '[-r, --required-only] <query-type> <parameters> ...'


if __name__ == '__main__':
    main()
