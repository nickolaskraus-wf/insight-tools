import sys

from datadog import api

from datadog_wrapper import Datadog


def main():
    Datadog()

    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    metric = sys.argv[1]
    tags = sys.argv[2]

    api.Metric.send(metric=metric, points=1, tags=tags)


def usage():
    print 'usage: get_metric.py [metric] [tags]'


if __name__ == '__main__':
    main()
