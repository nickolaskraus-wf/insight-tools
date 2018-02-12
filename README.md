# insight-tools
Python scripts for automating manual tasks.

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

In order to use these scripts, you will need to create `settings.py`:

`settings.py`

```python
LOCAL_COOKIE = 'user.name@workiva.com:True'
STAGING_COOKIE = ''
INCOMING_GCP_ERRORS_PATH = '/api/v1/hubble/incoming_gcp_errors'
PROCESS_ERRORS_PATH = '/cron/create_tasks_to_process_errors'
INSIGHT_STAGING_BASE_URL = 'https://w-insight-staging.appspot.com'
```

`STAGING_COOKIE` can be found in the Chrome Developer Tools:
**⇧+⌘+c** > **Application** > **Cookies** > **SACSID**

In addition, these scripts share the following flags:

```
-l | --local      send error to local instance (i.e. `localhost:8080`)
-s | --staging    send error to staging instance (i.e. `w-insight-staging.appspot.com`)
```

```bash
python simulate_gcp_error.py [-l | --local] [-s | --staging] <project>
```

* Create a GCP error for `<project>`

```bash
python simulate_kinesis_error.py [-l | --local] [-s | --staging] <service>
```

* Create a Kinesis error for `<service>`

```bash
python simulate_new_gcp_error.py [-l | --local] [-s | --staging] <project>
```

* Create a 'New' error for `<project>`

```bash
python simulate_new_kinesis_error.py [-l | --local] [-s | --staging] <service>
```

* Create a 'New' error for `<service>`

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