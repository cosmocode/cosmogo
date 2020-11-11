#!/usr/bin/env python

import argparse
import os
import sys
import time

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def main(filepath, warning, critical):
    try:
        mtime = os.path.getmtime(filepath)
    except os.error as error:
        return report(UNKNOWN, error)

    now = time.time()
    seconds = now - mtime
    message = '%s is %.1fs old.' % (filepath, seconds)

    if seconds < warning:
        return report(OK, message)
    elif seconds < critical:
        return report(WARNING, message)
    else:
        return report(CRITICAL, message)


def report(status, message):
    print(message)
    sys.exit(status)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--filepath', dest='filepath', required=True,
                        help='Path to the monitoring file written by the celery monitoring task.')
    parser.add_argument('-w', '--warning', dest='warning', type=int, default=5 * 60,
                        help='Number of seconds counted as warning.')
    parser.add_argument('-c', '--critical', dest='critical', type=int, default=10 * 60,
                        help='Number of seconds counted as critical.')

    arguments = parser.parse_args()

    main(**vars(arguments))
