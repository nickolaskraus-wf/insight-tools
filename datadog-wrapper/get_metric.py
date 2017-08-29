import datetime
import json

from datadog import api

from datadog_wrapper import Datadog


def main():
    datadog = Datadog()

    epoch = datetime.datetime.utcfromtimestamp(0)

    # start time = beginning of current day
    start_dt = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0,
                                                  microsecond=0)
    start_epoch = (start_dt - epoch).total_seconds()

    # end time = current time
    end_dt = datetime.datetime.utcnow()
    end_epoch = (end_dt - epoch).total_seconds()

    query = 'sum:insight.test_api{*}.rollup(sum, 60)'
    payload = api.Metric.query(start=start_epoch, end=end_epoch,
                               metric='insight.test_api', points=1, query=query)

    print json.dumps(payload, indent=2)


if __name__ == '__main__':
    main()
