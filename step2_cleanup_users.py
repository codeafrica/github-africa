#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json
import logging

from africa_data import countries

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
hdlr = logging.FileHandler('cleaned_up.log')
fmt = logging.Formatter('%(message)s')
hdlr.setFormatter(fmt)
logger.addHandler(hdlr)

UNKNOWN = u"Unknown"
DEBUG = False

all_users = json.load(open('step1.json'))
bads = []


def country_city_by_location(location):
    ll = location.lower()
    country_matches = []
    city_matches = []

    for ccode, cc in countries.items():
        for ct in cc.get('patterns'):
            for ct_name in ct.get('patterns', [ct.get('name')]):
                if ct_name.lower() in location.lower():
                    city_matches.append((ccode, ct.get('name')))
        for cc_name in cc.get('names', [ct.get('name')]):
            if cc_name.lower() in location.lower():
                country_matches.append(ccode)

    city_matches = list(set(city_matches))
    country_matches = list(set(country_matches))

    err = (None, None)

    # HACKS
    if "benin" in ll and "city" in ll:
        return 'NG', "Benin City"

    if "cape town" in ll:
        if not "Capte Town" in [x[1] for x in city_matches]:
            city_matches.append(('ZA', "Cape Town"))

    if 'africa' in ll and not 'south' in ll:
        while True:
            try:
                country_matches.remove('ZA')
            except ValueError:
                break

    if ('addis' in ll and 'ababa' in ll
        ) or 'rabat' in ll:
        while True:
            try:
                city_matches.remove(('NG', 'Aba'))
            except ValueError:
                break

    if 'kampala' in ll or 'uganda' in ll:
        while True:
            try:
                city_matches.remove(('TD', 'Pala'))
            except ValueError:
                break

    if 'nigeria' in ll:
        while True:
            try:
                country_matches.remove('NE')
            except ValueError:
                break

    # Saint Louis in Senegal and Missouri/USA
    if 'saint' in ll and 'louis' in ll \
        and (not 'sn' in ll or not 'senegal' in ll or not 'sénégal' in ll):
        return err

    # Man vs Isle of Man
    if 'isle of man' in ll:
        return err

    if 'juba' in ll:
        while True:
            try:
                country_matches.remove('SD')
            except ValueError:
                break

    # Joar Sahara in Bangladesh
    if 'sahara' in ll and 'joar' in ll:
        return err

    if 'verde' in ll and (not 'cape' in ll and not 'cabo' in ll):
        return err

    # Praia Grande, Brazil
    if 'praia' in ll and 'grande' in ll:
        return err

    # Tripoli in Lebanon
    if 'tripoli' in ll and 'lebanon' in ll:
        return err

    # Lagos, Chile
    if 'lagos' in ll and 'chile' in ll:
        return err

    if 'lagos' in ll and 'juan' in ll:
        return err

    if 'lagos' in ll and ('pt' in ll or 'portugal' in ll or 'island' in ll):
        return err

    if 'drc' in ll and 'madrid' in ll:
        return err

    # Monrovia, CA
    if 'monrovia' in ll and ('ca' in ll or 'california' in ll or 'us' in ll):
        return err

    # Saint Maurice
    if 'maurice' in ll and 'saint' in ll:
        return err

    # more than ile maurice
    if 'maurice' in ll and len(ll) > 13:
        return err

    # Mali / Somalia
    if 'somali' in ll:
       while True:
            try:
                country_matches.remove('ML')
            except ValueError:
                break

    # Cape Elisabeth in Maine
    if 'elizabeth' in ll and ('cape' in ll or 'maine' in ll \
        or 'nj' in ll or 'nc' in ll or 'co' in ll):
        return err

    # Alexandria, Virginia
    if 'alexandria' in ll and ('virginia' in ll or 'va' in ll):
        return err

    # DR Congo and RD Congo
    if 'congo' in ll and ('rd' in ll or 'dr' in ll):
        while True:
            try:
                country_matches.remove('CG')
            except ValueError:
                break
        country_matches.append('CD')

    # basically, we found a single match on city
    if len(city_matches) == 1:
        if len(country_matches) == 0 \
            or (len(country_matches) == 1
                and country_matches[-1] == city_matches[-1][0]):
            return city_matches[-1]
        elif city_matches[-1][0] in country_matches:
            return city_matches[-1]

    # single match on country
    elif len(city_matches) == 0 and len(country_matches) == 1:
        return country_matches[-1], None

    # multiple locations
    elif len(city_matches) > 1 or len(country_matches) > 1:
        # pick first city that matches a country
        if len(city_matches):
            for cc, ct in city_matches:
                if cc in country_matches:
                    return cc, ct
        # pick first country
        if len(country_matches):
            return country_matches[0], None
        # pick what's left: a city
        return city_matches[0]

    if DEBUG:
        print(len(city_matches))
        print(len(country_matches))

        from pprint import pprint as pp ; pp(city_matches)
        from pprint import pprint as pp ; pp(country_matches)

    country_code = None
    city_name = None

    return country_code, city_name


def guess_location(user):

    country_code, city_name = country_city_by_location(user.get('location'))

    if country_code is None:
        bads.append(user)
        return None

    if city_name is not None:
        latitude, longitude = [(x.get('latitude'), x.get('longitude'))
                    for x in countries.get(country_code).get('patterns')
                    if city_name in x.get('patterns', []) + [x.get('name')]][0]
    else:
        latitude = countries.get(country_code, {}).get('latitude')
        longitude = countries.get(country_code, {}).get('longitude')

    try:
        country_name = countries.get(country_code).get('name')
    except AttributeError:
        return None

    del(user['country'])
    del(user['city'])
    user.update({'country_code': country_code,
                 'country_name': country_name,
                 'city_name': city_name,
                 'has_city': city_name is not None,
                 'latitude': latitude,
                 'longitude': longitude,
                 'id_int': int(user.get('id').split('-', 1)[1])})
    return user

# DEBUG = True

if DEBUG:
    from pprint import pprint as pp ; pp(country_city_by_location(u"San Juan de los Lagos"))
    exit(0)


failed = []
valid_users = []
existing = []
unique_users = []

for user in all_users:
    new_user = guess_location(user)
    if new_user is None:
        continue
    userdesc = (u"%(country)s/%(city)s: @%(user)s: %(location)s"
                % {'country': new_user.get('country_name'),
                   'city': new_user.get('city_name'),
                   'user': new_user.get('username'),
                   'location': new_user.get('location')})
    if new_user.get('country_name') == UNKNOWN:
        failed.append(userdesc)
    else:
        valid_users.append(new_user)
        logger.info(userdesc)

for fail in failed:
    logger.info(fail)
logger.info("%d failed users" % len(failed))
logger.info("%d success users" % len(all_users))

for bad in bads:
    while True:
        try:
            all_users.remove(bad)
        except ValueError:
            break

for user in valid_users:
    if user['username'] in existing:
        continue
    unique_users.append(user)
    existing.append(user['username'])

json.dump(unique_users, open('step2.json', 'w'))
