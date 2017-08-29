from datadog import api

from datadog_wrapper import Datadog


def main():
    datadog = Datadog()

    api.Metric.send(metric='insight.test_api', points=1)


if __name__ == '__main__':
    main()
