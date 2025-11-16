#-----------------------------------------------------------------------
# testregdetailsgiven.py
# Authors: Nicole Deng and Ziya Momin
#-----------------------------------------------------------------------

"""
Browser automation test script for registrar class details
 functionality.
"""

import sys
import time
import argparse
import playwright.sync_api

MAX_LINE_LENGTH = 72
UNDERLINE = '-' * MAX_LINE_LENGTH

def get_args():
    """
    Parse command-line arguments for the browser test and returns
    a tuple with the server URL and browser type.
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

def print_flush(message):
    """
    Print a message and flush stdout for real-time output.
    """
    print(message)
    sys.stdout.flush()

def run_test(server_url, browser_process, classid):
    """
    Execute a single browser test for class details model.
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


def main():
    """
    Main function that runs browser tests for class details
    functionality.
    """
    server_url, browser = get_args()

    with playwright.sync_api.sync_playwright() as pw:

        if browser == 'chrome':
            browser_process = pw.chromium.launch()
        else:
            browser_process = pw.firefox.launch()

        run_test(server_url, browser_process, '8321')

        # normal class
        run_test(server_url, browser_process, '8321')

        
        for classId in ['7842', '7850', '7865', '7872', '7873']:
            run_test(server_url, browser_process, classId)

        # no professors
        for classId in ['7859', '7879', '7886', '7935', '8036']:
            run_test(server_url, browser_process, classId)

        # crosslisted courses
        for classId in ['7838', '7839', '7840', '7841', '7842']:
            run_test(server_url, browser_process, classId)

        # long descriptions
        for classId in ['7863', '8028', '8063', '8291', '8667']:
            run_test(server_url, browser_process, classId)

        # multiple crosslistings and professors
        run_test(server_url, browser_process, '8361')

        # empty or whitespace class IDs
        for classId in ['', ' ', '   ', '\t', '\n']:
            run_test(server_url, browser_process, classId)

        # long class IDs
        run_test(server_url, browser_process, '123456789012345678901234567890')

        # special characters in class IDs
        for classId in ['!@#$%', 'ABC#123', '123_456', 'class-8321']:
            run_test(server_url, browser_process, classId)

        # repeated queries
        for i in range(3):
            run_test(server_url, browser_process, '8321')

        # bad input
        for classId in [' 8321', '8321 ', ' 8321 ']:
            run_test(server_url, browser_process, classId)

        # missing database
        if os.path.exists('reg.sqlite'):
            shutil.copy('reg.sqlite', 'reg_backup.sqlite')
            os.remove('reg.sqlite')  
            run_test(server_url, browser_process, '8321')
            shutil.copy('reg_backup.sqlite', 'reg.sqlite') 

        # corrupted database
        if os.path.exists('reg.sqlite'):
            shutil.copy('reg.sqlite', 'reg_backup.sqlite')
            with open('reg.sqlite', 'w') as f:
                f.write('CORRUPTED DATA')
            run_test(server_url, browser_process, '8321')
            shutil.copy('reg_backup.sqlite', 'reg.sqlite')       

if __name__ == '__main__':
    main()
