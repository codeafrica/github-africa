#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json

# pip install path.py
from path import path

CSV_KEYS = [
    "followers_count",
    "language",
    "fullname",
    "login",
    "type",
    "created",
    "repos",
    "username",
    "created_at",
    "location",
    "followers",
    "id",
    "public_repo_count",
    "name",
    "country"]
NA = u""
users_dir = path(u'users')
output = open('users.csv', 'w')


def write(text):
    output.write((text + u"\n").encode('utf-8'))


def cleanup(text):
    if text is None:
        text = NA
    return u'"%s"' % unicode(text)

write(u",".join(CSV_KEYS))

# user's json exports in users/directory
for country_json_file in users_dir.walkfiles('*.json'):
    country_name = country_json_file.rsplit('.json', 1)[0].split('users/')[1]
    with open(country_json_file, 'r') as country_file:
        country_data = json.load(country_file)

    for user in country_data['users']:
        user.update({"country": country_name})

        write(u",".join([cleanup(user.get(key, None)) for key in CSV_KEYS]))
output.close()
