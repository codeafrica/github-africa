#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging
import json

import requests
from requests.auth import HTTPBasicAuth

from secret import CLIENT_ID, CLIENT_SECRET, GITHUB_USERNAME, GITHUB_PASSWORD

logger = logging.getLogger(__name__)

payload = {
    "scopes": [
        "public_repo"
    ],
    "note": "codeafrica script",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

req = requests.post("https://api.github.com/authorizations",
                    data=json.dumps(payload),
                    auth=HTTPBasicAuth(GITHUB_USERNAME, GITHUB_PASSWORD))

from pprint import pprint as pp ; pp(req.headers)

try:
    resp = json.loads(req.text)
except:
    resp = req.text
from pprint import pprint as pp ; pp(resp)

if 'token' in resp:
    print("!!! Run the following in your shell:")
    print('export GITHUB_TOKEN="{}"'.format(resp['token']))
