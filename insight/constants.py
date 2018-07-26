# Global
BASE_URL_LOCAL = 'http://localhost:8080'
BASE_URL_STAGING = 'https://w-insight-staging.appspot.com'

# Apollo
START_RUNNING_APOLLO = '/tasks/start_running_apollo'

# Hubble
INCOMING_GCP_ERRORS = '/api/v1/hubble/incoming_gcp_errors'
INCOMING_KINESIS_ERRORS = '/api/v1/hubble/incoming_errors'
PROCESS_ERRORS_PATH = '/cron/create_tasks_to_process_errors'
SERVICE_SUFFIX = ['-prod', '-eu', '-demo', '-sandbox', '-wk-dev', '-eu']
TIME_FORMAT_DEFAULT_DATETIME = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT_GCP_ERROR = '%Y-%m-%dT%H:%M:%S.0000Z'
TIME_FORMAT_GCP_RAW_ERROR = '%Y-%m-%dT%H:%M:%S.%fZ'
TIME_FORMAT_KINESIS_ERROR = '%Y/%m/%d %H:%M:%S'
TIME_FORMAT_KINESIS_RAW_ERROR = '%Y-%m-%dT%H:%M:%S.%fZ'
TIME_FORMAT_NO_MICRO_SEC = '%Y-%m-%dT%H:%M:%S.000-00:00'
DEFAULT_GCP_FILE = 'logs/default_gcp.json'
DEFAULT_KINESIS_FILE = 'logs/default_kinesis.json'
