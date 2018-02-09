"""
Description:
    Creates an issue or a sub-task from a JSON representation.

    If the command is executed with the '--issue-config' (abbr. -i) option, a
    request is made to the Jira API using the configuration file provided by
    the user. If the command is executed with the '--generate-skeleton' option,
    the /rest/api/2/issue/createmeta API is used to generate a skeleton for a
    configuration file containing the required fields and applicable values.

Usage:
  Options:
    -i, --issue-config     the issue's configuration information
    --generate-skeleton    prints a JSON skeleton of the request body to stand-
      <sparse>, <detailed> ard output without sending an API request. If pro-
                           vided with the value 'sparse', the request body only
                           contains valid values. If provided with the value
                           'detailed', the request body contains information
                           about the given fields. The request body is, how-
                           ever, invalid regardless.

  Arguments
    issuetypeIds      issue type IDs
    issuetypeNames    issue type names
    projectIds        project IDs
    projectKeys       project keys

  Examples:

    python create_issue.py --generate-skeleton sparse projectKeys IN issuetypeNames Bug

      * Generate a skeleton JSON request for project IN and issuetype Bug

Jira Cloud Rest API

POST /rest/api/2/issue

Creates an issue or a sub-task from a JSON representation.

You can provide two parameters in request's body: update or fields. The fields,
that can be set on an issue create operation, can be determined using the

    GET /rest/api/2/issue/createmeta

resource. If a particular field is not configured to appear on the issue's
Create screen, then it will not be returned in the createmeta response. A field
validation error will occur if such field is submitted in request.

Creating a sub-task is similar to creating an issue with the following differ-
ences:

    1. issueType field must be set to a sub-task issue type (use
    /issue/createmeta to find sub-task issue types), and
    2. You must provide a parent field with the ID or key of the parent issue.

App scope required: WRITE
Response content type: application/json
"""
import json
import os
import sys

from api import jira_fetch


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    options = {}

    for x, arg in enumerate(sys.argv):
        if arg in ('-i', '--issue-config'):
            options['issue_config'] = True
            try:
                options['file'] = '{}/{}'.format(
                    os.path.dirname(os.path.abspath(__file__)),
                    sys.argv[x + 1])
                if not os.path.isfile(options['file']):
                    print('Error: File does not exist.')
                    sys.exit(1)
            except IndexError:
                print('Error: No input file provided.')
                sys.exit(1)
        if arg == '--generate-skeleton':
            options['generate_skeleton'] = True
            options['is_sparse'] = True
            try:
                if sys.argv[x + 1] == 'detailed':
                    options['is_sparse'] = False
            except IndexError:
                continue

    if len(options) == 0:
        print('Error: None or invalid option.')
        usage()
        sys.exit(1)

    if len(sys.argv) > len(options):
        if (len(sys.argv) - len(options)) % 2 != 1:
            print('Error: Incorrect number of command line arguments.')
            usage()
            sys.exit(1)

    if options.get('generate_skeleton'):

        arguments = sys.argv[len(options) + 1:]

        if len(arguments) < 4:
            print('Error: Must provide arguments: <projectIds | projectKeys> '
                  '<issuetypeIds | issuetypeNames>.')
            usage()
            sys.exit(1)

        createmeta_url = build_url('/rest/api/2/issue/createmeta', arguments,
                                   True)

        response = jira_fetch(createmeta_url)

        print 'Status:'
        print response.status_code
        print 'Response:'
        try:
            parsed_reponse = parse_response(response.content, True)
            skeleton = generate_skeleton(parsed_reponse, options['is_sparse'])
            print json.dumps(skeleton, indent=4, sort_keys=True)
        except ValueError as e:
            print 'Error: {}'.format(e)
    else:
        data = json.load(open(options['file']))
        result = jira_fetch('/rest/api/2/issue/', data=json.dumps(data),
                            method='POST')

        print 'Status:'
        print result.status_code
        print 'Response:'
        try:
            parsed = json.loads(result.content)
            print json.dumps(parsed, indent=4, sort_keys=True)
        except ValueError as e:
            print 'Error: {}'.format(e)
            print result.text


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


def generate_skeleton(response, is_sparse):
    skeleton = {}

    try:
        fields = response['projects'][0]['issuetypes'][0]['fields']

        if is_sparse:
            for field in fields:
                _type = ''
                schema = fields[field].get('schema')
                if schema:
                    _type = schema.get('type')
                if _type == 'string':
                    skeleton[field] = ''
                elif _type == 'array':
                    skeleton[field] = []
                else:
                    skeleton[field] = {}
                allowed_values = fields[field].get('allowedValues')
                if allowed_values:
                    for dict in allowed_values:
                        if _type == 'array':
                            skeleton[field].append(dict)
                        else:
                            if skeleton[field]:
                                for old, new in zip(skeleton[field], dict):
                                    dict[new] = '{} | {}'.format(
                                        skeleton[field][old], dict[new])
                                skeleton[field] = dict
                            else:
                                skeleton[field] = dict

        else:
            for field in fields:
                _type = ''
                schema = fields[field].get('schema')
                if schema:
                    _type = schema.get('type')
                skeleton[field] = {}
                allowed_values = fields[field].get('allowedValues')
                if allowed_values:
                    skeleton[field]['allowedValues'] = []
                    for dict in allowed_values:
                        skeleton[field]['allowedValues'].append(dict)
                if allowed_values:
                    skeleton[field]['allowedValues'] = []
                    for dict in allowed_values:
                        if _type == 'array':
                            skeleton[field]['allowedValues'].append(dict)
                        else:
                            if skeleton[field]['allowedValues']:
                                for old, new in zip(
                                        skeleton[field]['allowedValues'][0],
                                        dict):
                                    dict[new] = '{} | {}'.format(
                                        skeleton[field]['allowedValues'][0][
                                            old], dict[new])
                                skeleton[field]['allowedValues'][0] = dict
                            else:
                                skeleton[field]['allowedValues'].append(dict)
                skeleton[field]['type'] = _type
                skeleton[field]['name'] = fields[field].get('name')
                skeleton[field]['hasDefaultValue'] = fields[field].get('hasDefaultValue')

    except (IndexError, KeyError) as e:
        print 'Failed to parse response. Error: {}'.format(e)

    skeleton = {'fields': skeleton}

    return skeleton


def usage():
    print 'usage: create_issue.py [-i, --issue-config <file>] ' \
          '[--generate-skeleton <sparse>, <detailed>]' \
          '<projectIds | projectKeys> <issuetypeIds | issuetypeNames>'


if __name__ == '__main__':
    main()
