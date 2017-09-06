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

    now = datetime.datetime.utcnow()
    date = now.strftime('%m/%d/%Y')
    start = int(unix_time((now - datetime.timedelta(seconds=1)).replace(
        microsecond=0)))
    end = int(unix_time(now.replace(microsecond=0)))

    payload = api.Metric.query(start=start, end=end,
                               metric='insight.test_api', query=query)

    print json.dumps(payload, indent=2)

    for series in payload['series']:
        print 'Scope: ' + series['scope']
        print 'Total metrics: ' + str(sum_metrics(series))


def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


def sum_metrics(series):
    total = 0
    for point in series['pointlist']:
        total += point[1] or 0

    return int(total)


def usage():
    print 'usage: test_in_2365.py [query]'


if __name__ == '__main__':
    main()
