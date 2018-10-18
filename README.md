# insight-tools
insight-tools comprises a collection of Python modules for automating manual tasks in Insight.

[![codecov](https://codecov.io/gh/nickolaskraus-wf/insight-tools/branch/master/graph/badge.svg)](https://codecov.io/gh/nickolaskraus-wf/insight-tools)

## Installation
```bash
pip install -r requirements.txt
```

## Commands

### base64

```bash
python base64_decode.py
```

* Prints the base64 decoded contents of the clipboard to standard out.

### cloud-storage

```bash
python manage_buckets.py
```

* Proof of Concept for Google Cloud Storage API.

```bash
python parse_usage_data.py
```

* Work In Progress for accessing Google Cloud Storage API and parsing usage data.

### datadog

```bash
datadog_wrapper.py
```

* Wrapper for Datadog API initialization

```bash
python get_metric.py <query>
```

* Get Datadog metrics for `<query>` for the last minute
Datadog API: `GET https://app.datadoghq.com/api/v1/query`

```bash
python get_metric.py <metric> <tags>
```

* Send Datadog metrics for `<metric>`  with `<tags>`
Datadog API: `POST https://app.datadoghq.com/api/v1/series`

```bash
python test_in_2365.py <query>
```

* Test IN-2365; get all metrics for a project in [query] for 2017-9-6

### hubble

In order to use this script, you will need to create `settings.py`:

`settings.py`

```python
COOKIE_LOCAL = 'user.name@workiva.com:True'
COOKIE_STAGING = ''
```

`COOKIE_STAGING` can be retrieved from the **Chrome Developer Tools**. After logging into https://w-insight-staging.appspot.com/:
**⇧+⌘+c** > **Application** > **Cookies** > **SACSID**

For help information, run:

```bash
python simulate_error.py -h
```

### jira

In order to use these scripts, you will need to create `settings.py`:

`settings.py`

```python
JIRA_HOST = 'https://jira.atl.workiva.net'
JIRA_USER = 'insight_user'
JIRA_PASS = ''
```

```bash
python create_issue.py [-i, --issue-config <file>]
                       [--generate-skeleton <sparse>, <detailed>]
                       <projectIds | projectKeys> <issuetypeIds | issuetypeNames>
```

* Creates an issue or a sub-task from a JSON representation.

If the command is executed with the `--issue-config` (abbr. `-i`) option, a request is made to the Jira API using the configuration file provided by the user. If the command is executed with the `--generate-skeleton` option, the `/rest/api/2/issue/createmeta` API is used to generate a skeleton for a configuration file containing the required fields and applicable values.

```bash
python get_create_issue_meta.py [-s, --show-fields] [-r, --required-only] [-d, --no-default] \
                                <query-type> <parameters> ...
```

* Returns the metadata for creating issues.

```bash
python get_issue_status.py <issue>
```

* Returns a full representation of the issue for the given issue key.
