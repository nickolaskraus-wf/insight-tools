import datetime
import json
import sys

from datadog import api

from datadog_wrapper import Datadog


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    query = sys.argv[1]

    Datadog()

    epoch = datetime.datetime.utcfromtimestamp(0)

    # start time = beginning of current day
    start_dt = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0,
                                                  microsecond=0)
    start_epoch = (start_dt - epoch).total_seconds()

    # end time = current time
    end_dt = datetime.datetime.utcnow()
    end_epoch = (end_dt - epoch).total_seconds()

    payload = api.Metric.query(start=start_epoch, end=end_epoch,
                               metric='insight.test_api', query=query)

    print json.dumps(payload, indent=2)

    for series in payload['series']:
        print 'Scope: ' + series['scope']
        print 'Total metrics: ' + str(sum_metrics(series))


def sum_metrics(series):
    total = 0
    for point in series['pointlist']:
        total += point[1] or 0

    return int(total)


def usage():
    print 'usage: get_metric.py [query]'


if __name__ == '__main__':
    main()
