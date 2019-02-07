import base64
import json
import re

from google.appengine.api import urlfetch
from google.appengine.api import memcache
from api.services import settings, auth

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
MOBILE_PATTERN = re.compile(r"^(?:(?:00|\+)\s*47\s*)?(?:[0-9]\s*){8}$")


def _getValue(item):
    if 'value' in item:
        return item['value']
    else:
        return None


def _cleanMemberData(data):
    result = {}

    for key, item in data.items():
        if 'status' not in item or _getValue(item['status']) != 'Aktiv':
            continue

        emails, mobiles = set(), set()
        collect = {
            'unit': None,
            'patrol': None,
            'first_name': None,
            'last_name': None
        }

        for attr, val in item.items():
            val = unicode(_getValue(val))

            if attr in collect:
                collect[attr] = val
            elif EMAIL_PATTERN.match(val):
                emails.add(val.lower())
            elif MOBILE_PATTERN.match(val):
                mobiles.add(re.sub(r"\D", '', val)[-8:])

        names = [collect['first_name'], collect['last_name']]

        result[key] = {
            'enhet': collect['unit'],
            'patrulje': collect['patrol'],
            'navn': ' '.join(filter(None, names)),
            'mobil': list(mobiles),
            'epost': list(emails),
        }

    return result


def byPatrol(data):
    result = {}

    for key, item in data.items():
        result.setdefault(
            '/'.join(filter(None, [item['enhet'], item['patrulje']])), []
        ).append(item)

    for key, members in result.items():
        result[key] = sorted(members, key=lambda k: k['navn'])

    return result


def fetchFromApi():
    url = 'https://min.speiding.no/api/group/memberlist'

    data = memcache.get(url)
    if data is None:
        key = settings.get('MIN_SPEIDING_MEMBERS_KEY')
        try:
            result = urlfetch.fetch(url,
                                    headers={'Authorization': 'Basic %s' %
                                             base64.b64encode(key)},
                                    validate_certificate=True
                                    )

            if result.status_code == 200:
                raw = json.loads(result.content)
                data = _cleanMemberData(raw['data'])
                memcache.add(key=url, value=data, time=3600)
            else:
                raise Exception(result.status_code)

        except urlfetch.Error as ex:
            raise ex

    return _filter(data)


def _filter(data):
    user = auth.get_current_user()

    if user is None:
        return {}

    scopes = user.scopes('members')

    if len(scopes) < 1:
        return {}

    scope_re = re.compile(
        ('^(' + '|'.join(scopes) + ')$').lower().replace('*',
                                                         '.*'))

    return {key: val for key, val in data.iteritems() if scope_re.match(
        str(val['enhet']).lower() + '/' + str(val['patrulje']).lower())}


class Member(object):
    def all(self, req):
        data = fetchFromApi()
        return data

    def on_get(self, req, resp):
        resp.media = self.all(req)
