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

    # testing on 2017-9-6
    if now < datetime.datetime(2017, 9, 6, 23, 59, 59):
        # deploy time
        start_time = datetime.datetime(2017, 9, 6, 18, 26)
        end_time = (now - datetime.timedelta(minutes=10)).replace(second=0,
                                                                  microsecond=0)
    # testing after 2017-9-6
    else:
        # 00:00:00 of current day
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = (now - datetime.timedelta(minutes=10)).replace(second=0,
                                                                  microsecond=0)

    start_unix = int(unix_time(start_time))
    end_unix = int(unix_time(end_time))

    print start_time
    print end_time

    payload = api.Metric.query(start=start_unix, end=end_unix, query=query)

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
    print 'usage: get_metric.py [query]'


if __name__ == '__main__':
    main()
