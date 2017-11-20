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

* Prints the base64 contents of the clipboard

### cloud-storage

```bash
python manage_buckets.py
```

* PoC for Google Storage API

```bash
python parse_usage_data.py
```

* WIP for accessing Google Storage API and parsing usage data

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

## TODO
* Allow all variables to be command line arguments
* Use `/process_errors` endpoint instead of `/cron/create_tasks_to_process_errors`
* Fix `simulate_new_kinesis_error.py`