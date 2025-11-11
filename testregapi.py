#!/usr/bin/env python

#-----------------------------------------------------------------------
# testregapi.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

import sys
import json
import argparse
import pprint
import urllib.request

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

#-----------------------------------------------------------------------

def parse_args():

    parser = argparse.ArgumentParser(
        description='Test the ability of the reg application to '
            + 'handle requests for JSON documents')

    parser.add_argument(
        'serverURL', metavar='serverURL', type=str,
        help='the URL of the reg application')

    args = parser.parse_args()

    return args.serverURL

#-----------------------------------------------------------------------

def run_test(serverurl, request):

    pp = pprint.PrettyPrinter(width=MAX_LINE_LENGTH, sort_dicts=True)
    sys.stdout.flush()

    print(UNDERLINE)
    sys.stdout.flush()
    print(UNDERLINE)
    sys.stdout.flush()
    pp.pprint(request)
    sys.stdout.flush()
    print(UNDERLINE)
    sys.stdout.flush()
    try:
        with urllib.request.urlopen(serverurl + request) as flo:
            response = flo.read()
            json_doc = response.decode('utf-8')
            response = json.loads(json_doc)
        pp.pprint(response)
        sys.stdout.flush()

    except Exception as ex:
        print(sys.argv[0] + ': ' + str(ex), file=sys.stderr)

#-----------------------------------------------------------------------

def main():

    serverurl = parse_args()

    request = '/regoverviews?dept=cos'
    run_test(serverurl, request)

    request = '/regoverviews?dept=COS&coursenum=2&area=qr&title=intro'
    run_test(serverurl, request)

    # Add more tests here.

    request = '/regdetails?classid=8321'
    run_test(serverurl, request)

    # Add more tests here.

if __name__ == '__main__':
    main()
