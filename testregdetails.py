#-----------------------------------------------------------------------
# testregdetails.py
# Authors: Bob Dondero (original), Nicole Deng and Ziya Momin (modified)
#-----------------------------------------------------------------------

"""
Browser automation test script for registrar class details functionality.

This program uses Playwright to test the modal dialog functionality
that displays detailed class information. It clicks on class ID buttons
in the search results and validates that the details modal appears
with the correct information formatted in tables.
"""

import sys
import time
import argparse
import playwright.sync_api

#-----------------------------------------------------------------------

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

#-----------------------------------------------------------------------

def get_args():
    """
    Parse command-line arguments for the browser test.
    
    Returns:
        tuple: (server_url, browser_type)
            server_url (str): URL of the application to test
            browser_type (str): 'firefox' or 'chrome'
    """

    parser = argparse.ArgumentParser(
        description='Test the ability of the reg application to '
            + 'handle "primary" (class overviews) queries')

    parser.add_argument(
        'serverURL', metavar='serverURL', type=str,
        help='the URL of the reg application')

    parser.add_argument(
        'browser', metavar='browser', type=str,
        choices=['firefox', 'chrome'],
        help='the browser (firefox or chrome) that you want to use')

    args = parser.parse_args()

    return (args.serverURL, args.browser)

#-----------------------------------------------------------------------

def print_flush(message):
    """
    Print a message and immediately flush stdout for real-time output.
    
    Args:
        message (str): Message to print
    """

    print(message)
    sys.stdout.flush()

#-----------------------------------------------------------------------

def run_test(server_url, browser_process, classid):
    """
    Execute a single browser test for class details modal.
    
    Opens the registrar application, clicks on a specific class ID button
    to trigger the details modal, then captures and prints the content
    of both the class details and course details tables.
    
    Args:
        server_url (str): URL of the application to test
        browser_process: Playwright browser instance
        classid (str): Class ID to click and test
    """

    print_flush(UNDERLINE)

    try:
        page = browser_process.new_page()
        page.goto(server_url)

        link = page.get_by_text(classid).first
        link.click()

        page.wait_for_selector('#classDetailsTable')
        class_details_table = page.locator('#classDetailsTable')
        print_flush(class_details_table.inner_text())

        page.wait_for_selector('#courseDetailsTable')
        course_details_table = page.locator('#courseDetailsTable')
        print_flush(course_details_table.inner_text())

    except Exception as ex:
        print(str(ex), file=sys.stderr)


#-----------------------------------------------------------------------

def main():
    """
    Main function that runs browser tests for class details functionality.
    
    Launches a browser, tests multiple class IDs to ensure the modal
    details functionality works correctly for different classes.
    """

    server_url, browser = get_args()

    with playwright.sync_api.sync_playwright() as pw:

        if browser == 'chrome':
            browser_process = pw.chromium.launch()
        else:
            browser_process = pw.firefox.launch()

        run_test(server_url, browser_process, '8321')

        run_test(server_url, browser_process, '7838') 
        run_test(server_url, browser_process, '8308')  

if __name__ == '__main__':
    main()
