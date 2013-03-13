#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

'''
    Dumps the whole Github users Database

    Takes a great while as script must pause an hour after each 6000 users.
    With 3,900,000 users, it'd be 28days...
    When authenticating, it pauses after 500,000 users so 8h total!
    The output file is copiable at anytime as it is close after each write.
    It's content is valid JSON as long as you close the list (])
'''

import os
import json
import logging
import time

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

last_id = None
output = 'all_users.json_txt'
one_minute = 60
one_hour = one_minute * 60
min_remaining_tostop = 30
reqs = 0
reqs_limit = None
reqs_remaining = None
headers = {'Authorization': 'token %s' % GITHUB_TOKEN} if GITHUB_TOKEN else {}


def pause(duration):
    ''' basic sleep with periodic logging (to show progess) '''
    interval = 10
    tick = duration / interval
    for i in xrange(interval):
        logger.info(u"Pause (%dmn) Elapsed: %dmn" % (duration / one_minute,
                                                     tick * i / one_minute))
        time.sleep(tick)

with open(output, 'w') as f:
    f.write("[\n")

while True:
    if last_id is not None:
        params = {'since': last_id}
    else:
        params = None

    logger.info(u"Requesting 100 users from %s -- %s/%s"
                % (last_id, reqs_limit, reqs_remaining))
    req = requests.get('https://api.github.com/users',
                       params=params,
                       headers=headers)
    reqs += 1

    if not req.status_code == requests.codes.ok:
        logger.error(u"Received status code %d. Pausing 1h." % req.status_code)
        pause(one_hour)
        continue

    try:
        json_content = json.loads(req.content)
        last_id = json_content[-1].get('id')
    except:
        pass

    if json_content is not None:
        with open(output, 'a') as f:
            if reqs > 1:
                f.write(",\n")
            f.write(req.content[1:-1])
    del(json_content)

    if len(req.content) < 20:
        break

    reqs_limit = int(req.headers.get('X-RateLimit-Limit', 0))
    reqs_remaining = int(req.headers.get('X-RateLimit-Remaining', 0))

    if reqs_remaining <= min_remaining_tostop:
        logger.info("Reached %d requests over %d. Pausing one hour."
                    % (reqs_limit - reqs_remaining, reqs_limit))
        pause(one_hour)
    continue

with open(output, 'a') as f:
    f.write("\n]\n")
