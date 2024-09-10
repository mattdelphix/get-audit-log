# get_audit_log

## What is it

get_audit_log is a program that, using Delphix Continuous Compliance APIs permits to export CDE Audit log in JSON format, for SIEM purposes.
get_audit_log is written in Python, but no knowledge of Python is required unless you want to extend it.
It has been complied on CentOS 8 and should be compatible with RHEL 8.


get_audit_log stores data of latest executiion or end date (if explicilty specified) in a file named:

.last_audit_extract_ENGINE_FQDN

where ENGINE_FQDN is the value of --engine_fqdn

Next executions will use the last execution timestamp as a starting point for new extractions. If you want to reset extraction, simply delete the .last_audit_xxxx file and rerun wiuth our without a start date. 


## Syntax:

### get_audit_log --help 

prints out program syntax


### get_audit_log --version

prints out program version and stops


### get_audit_log --engine_fqdn 172.16.111.160 --username admin --password passwd_123 --output initial_extraction.json

prints in file initial_extraction.json the list of all audit records from 2000-01-01 up to the time of current execution.
Last date is stored into .last_audit_extract_172.16.111.160


### get_audit_log --engine_fqdn 172.16.111.160 --username admin --password passwd_123 --output initial_extraction.json --test_only

Test run that skips the use of  .last_audit_extract_172.16.111.160 and prints in file initial_extraction.json the list of all audit records from 2000-01-01 up to the time of current execution.
Last date is NOT stored into .last_audit_extract_172.16.111.160,  File is NOT deleted, so a new normal run will use it.


### get_audit_log --engine_fqdn 172.16.111.160 --username admin --password passwd_123  --start_date 2024-03-12T18:53:25.044 --end_date 2024-03-21T18:53:25.044 --engine_offset "+02:00" --output extraction.json

prints in file extraction.json the list of audit records fro start_date to end_date, forcing an offset



## Source version

Python 3.9 or higher

**Required packages**
- from typing import Optional, Tuple, List
- import requests
- import traceback
- import urllib3
- import argparse
- import os.path
- from datetime import datetime



### Known issues

No known issues at the moment.


## <a id="contribute"></a>Contribute

1.  Fork the project.
2.  Make your bug fix or new feature.
3.  Add tests for your code.
4.  Send a pull request.

Contributions must be signed as `User Name <user@email.com>`. Make sure to [set up Git with user name and email address](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup). Bug fixes should branch from the current stable branch. New features should be based on the `master` branch.

#### <a id="code-of-conduct"></a>Code of Conduct

This project operates under the [Delphix Code of Conduct](https://delphix.github.io/code-of-conduct.html). By participating in this project you agree to abide by its terms.

#### <a id="contributor-agreement"></a>Contributor Agreement

All contributors are required to sign the Delphix Contributor agreement prior to contributing code to an open source repository. This process is handled automatically by [cla-assistant](https://cla-assistant.io/). Simply open a pull request and a bot will automatically check to see if you have signed the latest agreement. If not, you will be prompted to do so as part of the pull request process.


## <a id="reporting_issues"></a>Reporting Issues

Issues should be reported in the GitHub repo's issue tab. Include a link to it.

## <a id="statement-of-support"></a>Statement of Support

This software is provided as-is, without warranty of any kind or commercial support through Delphix. See the associated license for additional details. Questions, issues, feature requests, and contributions should be directed to the community as outlined in the [Delphix Community Guidelines](https://delphix.github.io/community-guidelines.html).


## <a id="license"></a>License
```
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
```
Copyright (c) 2024 by Delphix. All rights reserved.
