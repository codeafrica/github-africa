#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import json
from dateutil import parser as du_parser
from datetime import datetime
import StringIO

import requests
import html5lib
from html5lib import treebuilders

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
headers = {'Authorization': 'token %s' % GITHUB_TOKEN} if GITHUB_TOKEN else {}

existing_users = json.load(open('step2.json'))

try:
    all_users = json.load(open('step3.json'))
except:
    all_users = []


def extend_user(user):

    print(user.get('username'))

    def get_activity_from_html(username):
        r = requests.get('https://github.com/%s' % username, headers=headers)

        parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
        dom = parser.parse(StringIO.StringIO(r.content))
        divs = dom.getElementsByTagName('div')

        total_dom = [d for d in divs if d.getAttribute('class') == 'col contrib-day'][0]

        total_str = total_dom.childNodes[1].firstChild.nodeValue
        total_dates = total_dom.childNodes[3].nodeValue.strip()
        total_start = du_parser.parse(total_dates.split('-')[0])
        total_end = du_parser.parse(total_dates.split('-')[1])

        long_dom = [d for d in divs if d.getAttribute('class') == 'col contrib-streak'][0]

        long_str = long_dom.childNodes[1].firstChild.nodeValue
        long_dates = long_dom.childNodes[3].nodeValue.strip()
        if long_dates == "Rock - Hard Place":
            long_start = None
            long_end = None
        else:
            long_start = du_parser.parse(long_dates.split('-')[0].strip())
            if long_start.year > total_end.year:
                long_start = datetime(long_start.year - 1, long_start.month, long_start.year.day)
            long_end = du_parser.parse(long_dates.split('-')[1].strip())
            if long_end.year > total_end.year:
                long_end = datetime(long_end.year - 1, long_end.month, long_end.year.day)

        return {'contrib_total_num': int(total_str.split()[0]),
                'contrib_total_start': total_start.isoformat(),
                'contrib_total_end': total_end.isoformat(),
                'contrib_long_num': int(long_str.split()[0]),
                'contrib_long_start': long_start.isoformat() if not long_start is None else None,
                'contrib_long_end': long_end.isoformat() if not long_end is None else None}

    def get_profile(user):
        r = requests.get('https://api.github.com/users/%s' % user.get('username'),
                         headers=headers)
        nd = {}
        data = json.loads(r.content)
        for col in data.keys():
            if 'url' in col and not col == 'avatar_url':
                continue
            if col in user.keys():
                continue
            nd.update({col: data[col]})
        return nd

    try:
        acitiviy = get_activity_from_html(user.get('username'))
    except:
        acitiviy = {}
    profile = get_profile(user)

    user.update(acitiviy)
    user.update(profile)

    return user

all_usernames = [u['username'] for u in all_users]
for user in existing_users:
    if user['username'] in all_usernames:
        continue
    all_users.append(extend_user(user))
    json.dump(all_users, open('step3.json', 'w'))

json.dump(all_users, open('step3.json', 'w'))

