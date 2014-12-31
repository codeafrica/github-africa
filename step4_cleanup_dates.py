#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json
from bson import json_util
from datetime import datetime


existing_users = json.load(open('step3.json'),
                           object_hook=json_util.object_hook)

for user in existing_users:
    for col, val in user.items():
        if isinstance(val, datetime):
            user.update({col: val.isoformat()})

json.dump(existing_users, open('step4.json', 'w'), indent=4)
