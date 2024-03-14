from typing import Optional, Tuple, List
import requests
import logging
import os
import traceback
import urllib3
import time
import argparse



# CONFIGURATION SECTION
valid_response_status_codes = [200, 201]
base_header = {'Content-Type': 'application/json'}
pageSize = 500
timeout=(30, 300)


# UNCOMMENT IT FOR DEBUG ON HTTPS LEVEL

# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1


# THIS IS TO DISABLE WARNINGS ON SELF SIGNED CA
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


base_url = None
def set_authorization(auth_key):
    base_header["Authorization"] = auth_key


def post_call(url :str, request_headers :dict, request_data: dict =None, files: dict=None) -> Tuple[bool, Optional[dict]]:
    try:
        if request_data:
            response = requests.post(url, headers=request_headers, json=request_data, timeout=timeout, verify=False)
        if files:
            response = requests.post(url, headers=request_headers, files=files, data=request_data, timeout=timeout, verify=False)
        if not request_data and not files:
            return False, None

        if response.status_code not in valid_response_status_codes:
            return False, None

        return True, response.json()

    except Exception as excp:
        print(traceback.format_exc())
        return False, None



def get_call(url :str, request_headers :dict, query_params :dict=None) -> Tuple[bool, Optional[List[dict]]]:
    '''
    Get all objects using page size defined in pageSize
    '''

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


def get_one_call(url :str, request_headers :dict, query_params :dict=None) -> Tuple[bool, Optional[dict]]:
    '''
    Get only one object - no pagination involved - url already should have an ID
    '''

    if query_params:
        response = requests.get(url, headers=request_headers, params=query_params, verify=False)
    else:
        response = requests.get(url, headers=request_headers, verify=False)

    if response.status_code not in valid_response_status_codes:
        return False, None

    return True, response.json()


def get_audit(base_url :str, auth_key :str) -> Tuple[bool, Optional[dict]]:
    '''
    Get audit entry
    '''

    set_authorization(auth_key)

    api_url = f"{base_url}/audit-logs"
    success, response = get_call(api_url, base_header)
    if not success:
        return False, None

    return True, response


def login(base_url :str, user :str, password :str) -> Tuple[bool, Optional[dict]]:
    '''
    login to engine
    '''
    
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


# Run example:
# python get_audit.py --engine_fqdn 172.16.190.100 --username admin --password Admin-12


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Running masking job with name')
    parser.add_argument('--engine_fqdn', type=str, help='engine fqdn')
    parser.add_argument('--username', type=str, help='username')
    parser.add_argument('--password', type=str, help='password')


    args = parser.parse_args()

    engine_fqdn = args.engine_fqdn
    username = args.username
    password = args.password

    base_url = f"https://{engine_fqdn}/masking/api"
    ret_status, response = login(base_url, username, password)
    if ret_status:
        auth_key = response["Authorization"] 

    ret_status, response = get_audit(base_url, auth_key)
    if ret_status:
        for audit_item in sorted(response, key=lambda audit_entry: audit_entry["auditId"]):
            print(audit_item)
    else:
        print("Problem with getting audit entries")
