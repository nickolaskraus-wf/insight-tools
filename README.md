# insight-tools
Python scripts for automating manual tasks.

## Installation
```bash
pip install -r requirements.txt
```

## Commands

```bash
python simulate_new_gcp_error.py [-l | --local] [-s | --staging] <project>
```

* Create a 'New' error for `<project>`

```bash
python simulate_gcp_error.py [-l | --local] [-s | --staging] <project>
```

* Create an error for `<project>`

```bash
python post_metric.py
```

* Post metric to Datadog

Datadog API: `POST https://app.datadoghq.com/api/v1/series`

```bash
python get_metric.py
```

* Get metric from Datadog

Datadog API: `GET https://app.datadoghq.com/api/v1/query`


## TODO
* Allow all variables to be command line arguments