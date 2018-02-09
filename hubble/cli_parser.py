#!/usr/bin/python

import argparse


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print(args.accumulate(args.integers))

    # # configure command line argument parser
    # parser = argparse.ArgumentParser(
    #     description='Simulate a Kinesis error log on Insight.')
    # group = parser.add_mutually_exclusive_group()
    # # service to which the error is sent
    # parser.add_argument('service',
    #                     help='service to which the error is sent')
    # # number of errors to send to Insight
    # parser.add_argument('-n', '--number', type=int, default=1,
    #                     help='number of errors to send')
    # # specify if error should be new
    # parser.add_argument('--new', action='store_true',
    #                     help='send new error')
    # # specify if error should be sent to local or staging Insight instance
    # group.add_argument('-l', '--local', action='store_true',
    #                     help='send to local instance')
    # group.add_argument('-s', '--staging', action='store_true',
    #                     help='send to staging instance')
    #
    # args = parser.parse_args()
    # print(args.accumulate(args.integers))


if __name__ == '__main__':
    main()
