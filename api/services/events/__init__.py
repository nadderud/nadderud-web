#!/usr/bin/env python

from google.appengine.ext import ndb
from .. import record


class Event(record.Record):
    navn = ndb.StringProperty(required=True)
    sted = ndb.StringProperty(required=False)
    start = ndb.DateTimeProperty(required=True)
    slutt = ndb.DateTimeProperty(required=True)
    enhet = ndb.StringProperty(required=True, default="")
    patrulje = ndb.StringProperty(required=True, default="")
    ansvar = ndb.StringProperty(required=False)
    info = ndb.StringProperty(required=False)

    settable = ['navn', 'sted', 'start', 'slutt',
                'enhet', 'patrulje', 'ansvar', 'info']
    filterable = ['enhet', 'semester']
    sort = [start, slutt]
