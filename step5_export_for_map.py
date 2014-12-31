#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging
import json
import unicodecsv as csv

from bson import json_util
from africa_data import countries

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

all_users = json.load(open('step4.json'),
                      object_hook=json_util.object_hook)

csv_file = open('github-users.csv', 'w')
headers = ['country_code', 'country_name',
           'city', 'latitude', 'longitude', 'nb_users', 'percent']
csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
csv_writer.writeheader()

nb_total_users = len(all_users)
logger.info("NB USERS: {}".format(nb_total_users))

pc_of_total = lambda num: num / nb_total_users

cities_map = {}
countries_map = {}

logger.info("Looping through users to build maps")
for user in all_users:
    logger.debug(user['username'])
    if user['city_name'] not in cities_map.keys():
        cities_map[user['city_name']] = {'nb_users': 0,
                                         'country_code': user['country_code'],
                                         'country_name': user['country_name'],
                                         'latitude': user['latitude'],
                                         'longitude': user['longitude']}
    cities_map[user['city_name']]['nb_users'] += 1

    if user['country_code'] not in countries_map.keys():
        countries_map[user['country_code']] = {
            'nb_users': 0,
            'name': user['country_name'],
            'latitude': countries[user['country_code']]['latitude'],
            'longitude': countries[user['country_code']]['longitude']}
    countries_map[user['country_code']]['nb_users'] += 1

logger.info("Looping through countries to write to CSV")
for country_code, country in countries_map.items():
    logger.debug(country['name'])
    csv_writer.writerow({
        'country_code': country_code,
        'country_name': country['name'],
        'city': "",
        'latitude': country['latitude'],
        'longitude': country['longitude'],
        'nb_users': country['nb_users'],
        'percent': pc_of_total(country['nb_users'])
    })

logger.info("Looping through cities to write to CSV")
for city_name, city in cities_map.items():
    logger.debug(city_name)
    if city_name is None:
        continue
    csv_writer.writerow({
        'country_code': city['country_code'],
        'country_name': city['country_name'],
        'city': city_name,
        'latitude': city['latitude'],
        'longitude': city['longitude'],
        'nb_users': city['nb_users'],
        'percent': pc_of_total(city['nb_users'])
    })

csv_file.close()

logger.info("NB USERS: {}".format(nb_total_users))
