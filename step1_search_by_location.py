#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import json
import logging
import copy

import requests
from requests.auth import HTTPBasicAuth

from africa_data import countries

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

output = 'step1.json'
one_minute = 60
one_hour = one_minute * 60
min_remaining_tostop = 30
reqs = 0
reqs_limit = None
reqs_remaining = None
headers = {}
TOKEN_AUTH = HTTPBasicAuth(GITHUB_TOKEN, "x-oauth-basic")


all_users = []


def add_to(search_term, all_users, country_stub, city=None):

    def users_from(location):
        complete = False
        page = 1
        users = []
        order = 'asc'
        while not complete:
            if page > 10:
                # well, we can't query anymore.
                if order == 'desc':
                    complete = True
                    continue
                order = 'desc'
                page = 1
            req = requests.get(
                'https://api.github.com/legacy/user/search/location:%s' %
                location,
                headers=headers, params={'start_page': page,
                                         'sort': 'joined',
                                         'order': order},
                auth=TOKEN_AUTH)
            page += 1
            try:
                jsusers = json.loads(req.content).get('users')
                if not len(jsusers):
                    complete = True
                    continue
                users += jsusers
            except:
                logger.warning("Failed to parse JSON:")
                logger.warning(req.content)
                complete = True

        return users

    json_users = users_from(search_term)

    if not len(json_users):
        return

    for user in json_users:
        logger.info("FOUND -- %s -- %s" % (user.get('username'),
                                           user.get('location')))
        user.update({'country': country_stub,
                     'city': city})
        all_users.append(user)

for country_code, country in countries.items():
    logger.info("COUNTRY: %s" % country.get('name'))

    country_stub = copy.copy(country)
    country_stub.update({'code': country_code})
    del(country_stub['patterns'])

    for city in country.get('patterns', []):
        logging.info("SEARCHING for city -- %s" % city.get('name'))
        for search_name in city.get('patterns', [city.get('name')]):
            add_to(search_name, all_users, country_stub, city)

    for name in country.get('names', []):
        logging.info("SEARCHING for country -- %s" % name)
        add_to(name, all_users, country_stub, None)

logger.info("Found %d records" % len(all_users))

json.dump(all_users, open(output, 'w'), indent=4)

logger.info("UNIQUE user accounts: %d" %
            len(list(set([u.get('username') for u in all_users]))))
