#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright (c) 2024 by Delphix. All rights reserved.
#
# Author  :  Marcin Przepiorowski
# Modified:  Matteo Ferrari
# Date    :  September 2024
#
# Get Delphix Continuous Compliance Engine Audit Log for a specific period
#
# Run example:
# python get_audit_log.py --engine_fqdn 172.16.190.100 --label Label1 --username admin --password Admin-12 --start_date --end_date
#
#        if start_date not specified, it is set to: 2000-01-01T00:00:00.000+00:00
#        if end_date not specified,   it is set to: 2099-01-01T00:00:00.000+00:00
#

from typing import Optional, Tuple, List
import requests
from urllib3.exceptions import InsecureRequestWarning
import certifi
import traceback
import urllib3
import argparse
import os.path
import json
import sys
# import logging
from datetime import datetime

# import time

# CONFIGURATION SECTION
valid_response_status_codes = [200, 201]
base_header = {'Content-Type': 'application/json'}
pageSize = 500
timeout = (30, 300)
script_version = "Version 1.4 - 09-09-2024"

# UNCOMMENT IT FOR DEBUG ON HTTPS LEVEL

# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# THIS IS TO DISABLE WARNINGS ON SELF SIGNED CA - NEW VERSION
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

base_url = None


def set_authorization(auth_key):
    base_header["Authorization"] = auth_key


def post_call(url: str, request_headers: dict, request_data: dict = None, files: dict = None) -> Tuple[
    bool, Optional[dict]]:
    global response
    try:
        if request_data:
            response = requests.post(url, headers=request_headers, json=request_data, timeout=timeout, verify=False)
        if files:
            response = requests.post(url, headers=request_headers, files=files, data=request_data, timeout=timeout,
                                     verify=False)
        if not request_data and not files:
            return False, None

        if response.status_code not in valid_response_status_codes:
            print("Status code: " + str(response.status_code))
            return False, None

        return True, response.json()

    except Exception as excp:
        print(traceback.format_exc())
        return False, None


def get_call(url: str, request_headers: dict, query_params: dict = None) -> Tuple[bool, Optional[List[dict]]]:
    #
    # Get all objects using page size defined in pageSize
    #
    global response

    if not query_params:
        query_params = dict()

    page_number = 1
    query_params["page_size"] = pageSize
    query_params["page_number"] = page_number
    total = 0
    return_list = list()

    while True:
        if query_params:
            response = requests.get(url, headers=request_headers, params=query_params, timeout=timeout, verify=False)
        else:
            response = requests.get(url, headers=request_headers, timeout=timeout, verify=False)

        # debug
        #print(f"Status code: {response.status_code}")
        #print(f"Status code: {response.text}")

        if response.status_code not in valid_response_status_codes:
            if "is outside of the acceptable range. The last page is" in response.text:
                return True, return_list
            return False, None

        response_obj = response.json()
        total = total + response_obj["_pageInfo"]["numberOnPage"]

        return_list.extend(response_obj["responseList"])
        if total >= response_obj["_pageInfo"]["total"]:
            break
        query_params["page_number"] = query_params["page_number"] + 1

    return True, return_list


def get_one_call(url: str, request_headers: dict, query_params: dict = None) -> Tuple[bool, Optional[dict]]:
    #
    # Get only one object - no pagination involved - url already should have an ID
    #

    if query_params:
        response = requests.get(url, headers=request_headers, params=query_params, verify=False)
    else:
        response = requests.get(url, headers=request_headers, verify=False)

    # debug
    #print(f"Status code: {response.status_code}")
    #print(f"Status code: {response.text}")

    if response.status_code not in valid_response_status_codes:
        print("Status code: " + str(response.status_code))
        return False, None

    return True, response.json()


def get_audit(base_url: str, auth_key: str) -> Tuple[bool, Optional[dict]]:
    #
    # Get audit entry
    #

    set_authorization(auth_key)

    api_url = f"{base_url}/audit-logs?start_time=" + start_audit_date + "&end_time=" + end_audit_date

    print("API URL     : " + api_url)

    success, response = get_call(api_url, base_header)
    if not success:
        return False, None

    return True, response


def login(base_url: str, user: str, password: str) -> Tuple[bool, Optional[dict]]:
    #
    # login to engine
    #

    api_url = f"{base_url}/login"
    request_data = dict()
    request_data['username'] = user
    request_data['password'] = password
    success, response = post_call(api_url, base_header, request_data)
    if not success:
        return False, None
    if 'Authorization' not in response or not response['Authorization']:
        return False, None

    return True, response


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract Continuous Compliance Engine Audit Log')
    parser.add_argument('--engine_fqdn', type=str, help='engine fqdn')
    parser.add_argument('--username', type=str, help='username')
    parser.add_argument('--password', type=str, help='password')
    parser.add_argument('--label', type=str, help='label to help filtering the log records')
    parser.add_argument('--start_date', type=str, help='start date for audit log')
    parser.add_argument('--end_date', type=str, help='end date for audit log')
    parser.add_argument('--engine_offset', type=str, help='engine offset (in the form "+00:00" or "-00:00"')
    parser.add_argument('--output', type=str, help='file name that will contain the log records')
    parser.add_argument('--version', action='store_true', help='prints version of this program')
    parser.add_argument('--test_only', action='store_true', help='test only execution. does not5 save last run info.')

    args = parser.parse_args()

    print("=====================================================================")
    print(" Delphix Continuous Compliance Audit Log extraction")
    print("=====================================================================")
    # set default start and end date if not specified

    if args.version:
        print(script_version)
        sys.exit(0)

    if not args.label:
        print("Error: label must be specified.")
        sys.exit(8)

    if not args.engine_fqdn:
        print("Error: engine name or IP must be specified.")
        sys.exit(8)

    if not args.username:
        print("Error: username must be specified.")
        sys.exit(8)

    if not args.password:
        print("Error: password must be specified.")
        sys.exit(8)

    if not args.output:
        print("Error: output filename must be specified.")
        sys.exit(8)

    if not args.engine_offset:
        args.engine_offset = "+00:00"

    if not args.start_date:
        args.start_date = "2000-01-01T00:00:00.000" + args.engine_offset
    else:
        args.start_date = args.start_date + args.engine_offset

    if not args.end_date:
        args.end_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + args.engine_offset
    else:
        args.end_date = args.end_date + args.engine_offset

    # args.end_date = "2099-01-01T00:00:00.000"+args.engine_offset

    engine_fqdn = args.engine_fqdn
    label = args.label
    username = args.username
    password = args.password
    auth_key = ""
    last_exec_file = ".last_audit_extract_" + engine_fqdn

    # read last execution from file
    if not args.test_only:
        if os.path.isfile(last_exec_file):
            with open(last_exec_file, 'r') as file:
                args.start_date = file.read()

    print("Engine      : " + args.engine_fqdn)
    print("Label       : " + args.label)
    print("Start       : " + args.start_date)
    print("End         : " + args.end_date)
    print("Output file : " + args.output)
    if args.test_only:
        print("***  TEST-ONLY Execution  ***")

    start_audit_date = requests.utils.quote(args.start_date)
    end_audit_date = requests.utils.quote(args.end_date)

    #
    # Execution
    #

    base_url = f"https://{engine_fqdn}/masking/api"

    ret_status, response = login(base_url, username, password)
    if ret_status:
        auth_key = response["Authorization"]
    else:
        print("Problem during login. Check engine type, user credentials and user role (must be admin)." )
        sys.exit(8)

    ret_status, response = get_audit(base_url, auth_key)
    if ret_status:
        f = open(args.output, "w")
        countr = 0
        for audit_item in sorted(response, key=lambda audit_entry: audit_entry["auditId"]):
            # enrich json with engine name
            audit_item2 = {**{"label": label}, **audit_item}
            final_audit_item = {**{"engine": engine_fqdn}, **audit_item2}
            countr = countr + 1
            f.write(json.dumps(final_audit_item) + '\n')
        f.close()
        print("Records out : " + str(countr))

        # write last execution
        if not args.test_only:
            with open(last_exec_file, "w") as f:
                f.write(args.end_date)

    else:
        print("Problem with getting audit entries.")
        sys.exit(8)
