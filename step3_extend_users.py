#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import json
import time
from dateutil import parser as du_parser
from datetime import datetime
import StringIO
import logging

import requests
from requests.auth import HTTPBasicAuth
import html5lib
from html5lib import treebuilders

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

last_id = None
one_minute = 60
one_hour = one_minute * 60
min_remaining_tostop = 30
reqs = 0
# reqs_limit = None
# reqs_remaining = None
headers = {}
TOKEN_AUTH = HTTPBasicAuth(GITHUB_TOKEN, "x-oauth-basic")


def check_limits(headers):
    reqs_limit = int(headers.get('X-RateLimit-Limit', 0))
    reqs_remaining = int(headers.get('X-RateLimit-Remaining', 0))

    if reqs_remaining <= min_remaining_tostop:
        logger.info("Reached %d requests over %d. Pausing one hour."
                    % (reqs_limit - reqs_remaining, reqs_limit))
        pause(one_hour)


def pause(duration):
    ''' basic sleep with periodic logging (to show progess) '''
    interval = 10
    tick = duration / interval
    for i in xrange(interval):
        logger.info(u"Pause (%dmn) Elapsed: %dmn" % (duration / one_minute,
                                                     tick * i / one_minute))
        time.sleep(tick)

existing_users = json.load(open('step2.json'))

try:
    all_users = json.load(open('step3.json'))
except:
    all_users = []


def getElementsByClassName(root, tag, className):
    return [e for e in root.getElementsByTagName(tag)
            if className in e.getAttribute('class')]


def extend_user(user):

    print(user.get('username'))

    def get_activity_from_html(username):
        r = requests.get('https://github.com/%s' % username,
                         headers=headers, auth=TOKEN_AUTH)

        if r.status_code == 404:
            return None

        parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        dom = parser.parse(StringIO.StringIO(r.content))
        divs = dom.getElementsByTagName('div')

        contrib_columns = [d for d in divs
                           if 'contrib-column' in
                           d.getAttribute('class')]

        if not len(contrib_columns):
            return {'contrib_total_num': 0,
                    'contrib_total_start': None,
                    'contrib_total_end': None,
                    'contrib_long_num': 0,
                    'contrib_long_start': None,
                    'contrib_long_end': None}

        total_str = getElementsByClassName(
            contrib_columns[0], "span",
            "contrib-number")[0].firstChild.nodeValue
        # logger.debug("total_str: {}".format(total_str))
        total_dates_dom = getElementsByClassName(
            contrib_columns[0], "span", "text-muted")[1]
        total_dates = "".join([n.nodeValue
                               for n in total_dates_dom.childNodes])
        # logger.debug("total_dates: {}".format(total_dates))

        total_start = du_parser.parse(total_dates.split(u'–')[0])
        total_end = du_parser.parse(total_dates.split(u'–')[1])
        # logger.debug("total_start: {}".format(total_start))
        # logger.debug("total_end: {}".format(total_end))

        long_str = getElementsByClassName(
            contrib_columns[1], "span",
            "contrib-number")[0].firstChild.nodeValue
        # logger.debug("long_str: {}".format(long_str))
        long_dates_dom = getElementsByClassName(
            contrib_columns[1], "span", "text-muted")[1]
        long_dates = "".join([n.nodeValue
                              for n in long_dates_dom.childNodes])
        # logger.debug("total_dates: {}".format(total_dates))
        # logger.debug("long_dates: {}".format(long_dates))

        if long_dates == "No recent contributions":
            long_start = None
            long_end = None
        else:
            long_start = du_parser.parse(long_dates.split(u'–')[0].strip())
            if long_start.year > total_end.year:
                long_start = datetime(long_start.year - 1,
                                      long_start.month, long_start.year.day)
            long_end = du_parser.parse(long_dates.split(u'–')[1].strip())
            if long_end.year > total_end.year:
                long_end = datetime(long_end.year - 1, long_end.month,
                                    long_end.year.day)

        return {
            'contrib_total_num': int(total_str.split()[0].replace(',', '')),
            'contrib_total_start': total_start.isoformat(),
            'contrib_total_end': total_end.isoformat(),
            'contrib_long_num': int(long_str.split()[0].replace(',', '')),
            'contrib_long_start':
                long_start.isoformat() if long_start is not None else None,
            'contrib_long_end':
                long_end.isoformat() if long_end is not None else None}

    def get_profile(user):
        r = requests.get(
            'https://api.github.com/users/%s' % user.get('username'),
            headers=headers, auth=TOKEN_AUTH)

        check_limits(r.headers)

        nd = {}
        data = json.loads(r.content)
        for col in data.keys():
            if 'url' in col and not col == 'avatar_url':
                continue
            if col in user.keys():
                continue
            nd.update({col: data[col]})
        return nd

    def get_orgs(username):
        orgs = {}
        r = requests.get('https://api.github.com/users/%s/orgs' % username,
                         headers=headers, auth=TOKEN_AUTH)

        check_limits(r.headers)

        data = json.loads(r.content)

        orgs.update({'orgs_num': len(data)})
        for i, org in enumerate(data):
            org_name = org.get('login')
            prefix = 'org%d_' % i
            rorg = requests.get('https://api.github.com/orgs/%s' % org_name,
                                headers=headers, auth=TOKEN_AUTH)

            check_limits(rorg.headers)

            data_org = json.loads(rorg.content)
            nd = {}
            for col in data_org.keys():
                if 'url' in col and not col == 'avatar_url':
                    continue
                nd.update({prefix + col: data_org[col]})
            orgs.update(nd)
        return orgs

    try:
        acitiviy = get_activity_from_html(user.get('username'))
    except Exception as e:
        logger.exception(e)
        raise
        acitiviy = {}
    from pprint import pprint as pp ; pp(acitiviy)

    if acitiviy is None:
        return None

    profile = get_profile(user)

    orgs = get_orgs(user.get('username'))

    user.update(acitiviy)
    user.update(profile)
    user.update(orgs)

    return user

# extend_user({'username': 'tensystems'})
# raise

all_usernames = [u['username'] for u in all_users]
for user in existing_users:
    if user['username'] in all_usernames:
        continue
    user_update = extend_user(user)
    if user_update is None:
        continue
    all_users.append(user_update)
    json.dump(all_users, open('step3.json', 'w'), indent=4)

json.dump(all_users, open('step3.json', 'w'), indent=4)
