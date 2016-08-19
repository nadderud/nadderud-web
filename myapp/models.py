#!/usr/bin/env python

from google.appengine.ext import ndb


class Unit(ndb.Model):
    name = ndb.StringProperty(required=True, default="")
    active = ndb.BooleanProperty(required=True, default=True)

    @classmethod
    def get_key_from_string(_, key_string):
        key_chain = ['Unit', 'root']
        for unit_name in key_string.split('/'):
            if unit_name:
                key_chain += ['Unit', unit_name.lower()]
        return ndb.Key(*key_chain)


class Event(ndb.Model):
    name = ndb.StringProperty(required=True, default="")
    location = ndb.StringProperty(required=True, default="")
    start_at = ndb.DateTimeProperty(required=True)
    end_at = ndb.DateTimeProperty(required=True)
    unit = ndb.KeyProperty(required=True, kind=Unit)
    responsibility = ndb.StringProperty(required=True, default="")
    remark = ndb.StringProperty(required=True, default="")

    @classmethod
    def query_unit(cls, unit_key):
        keys = [unit_key]
        while unit_key.parent():
            unit_key = unit_key.parent()
            keys += unit_key
        return cls.query_units(keys)

    @classmethod
    def query_units(cls, keys):
        return cls.query(cls.unit.IN(keys)).order(cls.start_at, cls.end_at)


class Article(ndb.Model):
    title = ndb.StringProperty(required=True, default="")
    author = ndb.StringProperty(required=True, default="")
    description = ndb.StringProperty(required=True, default="")
    body = ndb.TextProperty()
    unit = ndb.KeyProperty(required=True, kind=Unit)
    event = ndb.KeyProperty(kind=Event)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)


class Contact(ndb.Model):
    """Sub model for parents."""
    name = ndb.StringProperty()
    phone = ndb.StringProperty()
    email = ndb.StringProperty()


class Member(ndb.Model):
    name = ndb.StringProperty(required=True, default="")
    address = ndb.StringProperty(required=True, default="")
    postal_code = ndb.StringProperty(required=True, default="")
    postal_city = ndb.StringProperty(required=True, default="")
    phone = ndb.StringProperty(required=True, default="")
    mobile = ndb.StringProperty(required=True, default="")
    email = ndb.StringProperty(required=True, default="")
    unit = ndb.KeyProperty(kind=Unit)
    position = ndb.StringProperty()
    mother = ndb.StructuredProperty(Contact)
    father = ndb.StructuredProperty(Contact)
    trial_expires = ndb.DateTimeProperty()
    is_member = ndb.BooleanProperty(default=False)
    is_active = ndb.BooleanProperty(default=False)
    remark = ndb.TextProperty()
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)
