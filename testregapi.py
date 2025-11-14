#!/usr/bin/env python

#-----------------------------------------------------------------------
# testregapi.py
# Authors: Bob Dondero (original), Nicole Deng and Ziya Momin (modified)
#-----------------------------------------------------------------------

"""
Test script for the Registrar API endpoints.

This program tests the JSON API routes (/regoverviews and /regdetails)
of the registrar application by making HTTP requests and validating
the responses. It tests various input combinations and error conditions
to ensure the API behaves correctly according to the specification.
"""

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
    """
    Parse command-line arguments for the test script.
    
    Returns:
        str: The server URL to test against
    """

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
    """
    Execute a single API test by making an HTTP request and printing results.
    
    Args:
        serverurl (str): Base URL of the server to test
        request (str): API endpoint and query parameters to test
    """

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
    """
    Main function that runs comprehensive API tests.
    
    Tests both /regoverviews and /regdetails endpoints with various
    input combinations and error conditions including missing parameters,
    invalid data types, and non-existent records.
    """

    serverurl = parse_args()

    # Test regoverviews with various inputs
    request = '/regoverviews?dept=cos'
    run_test(serverurl, request)

    request = '/regoverviews?dept=COS&coursenum=2&area=qr&title=intro'
    run_test(serverurl, request)

    request = '/regoverviews?dept=&coursenum=&area=&title='
    run_test(serverurl, request)
    
    request = '/regoverviews?dept=COS&coursenum=333'
    run_test(serverurl, request)
    
    request = '/regoverviews?area=qr'
    run_test(serverurl, request)
    
    request = '/regoverviews?title=programming'
    run_test(serverurl, request)
    
    request = '/regoverviews?dept=NONEXISTENT'
    run_test(serverurl, request)

    request = '/regdetails?classid=8321'
    run_test(serverurl, request)

    request = '/regdetails?classid=99999'  
    run_test(serverurl, request)
    
    request = '/regdetails?classid=abc'    
    run_test(serverurl, request)
    
    request = '/regdetails'                 
    run_test(serverurl, request)
    
    request = '/regdetails?classid='        
    run_test(serverurl, request)

if __name__ == '__main__':
    main()
