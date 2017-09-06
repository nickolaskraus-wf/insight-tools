import os

from datadog import initialize

from settings import DATADOG_API_TOKEN, DATADOG_APP_TOKEN


class Datadog():
    def __init__(self):
        self.initialize(self)

    @staticmethod
    def initialize(self):
        try:
            host_name = os.environ['HTTP_HOST']
        except KeyError:
            host_name = ''
        options = {
            'api_key': DATADOG_API_TOKEN,
            'app_key': DATADOG_APP_TOKEN,
            'host_name': host_name
        }

        initialize(**options)
