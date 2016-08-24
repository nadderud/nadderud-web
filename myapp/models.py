#!/usr/bin/env python

from datetime import datetime, timedelta
from google.appengine.ext import ndb

from myapp import dateparser


def semester_from_date(start_at):
    semester = 'v'
    if start_at.timetuple().tm_yday > 222:  # 10 Aug
        semester = 'h'
    return semester + start_at.strftime('%y')


def strexist(str):
    return isinstance(str, unicode)


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
    semester = ndb.ComputedProperty(lambda self:
                                    semester_from_date(self.start_at))

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

    def from_multidict(self, mdict):
        if strexist(mdict.get('unit')):
            self.unit = ndb.Key(urlsafe=mdict.get('unit'))
        if strexist(mdict.get('event')):
            self.event = ndb.Key(urlsafe=mdict.get('event'))
        for item in ['name', 'location', 'responsibility', 'remark']:
            if strexist(mdict.get(item)):
                setattr(self, item, mdict.get(item))
        for item in ['start_at', 'end_at']:
            if strexist(mdict.get(item)):
                setattr(self, item, dateparser.multiparse(mdict.get(item)))
        if self.start_at and strexist(mdict.get('duration')):
            self.end_at = self.start_at + \
                timedelta(hours=float(mdict.get('duration')))

    def validate(self):
        errors = {}
        for item in ['unit', 'name', 'location', 'start_at', 'end_at']:
            if not getattr(self, item):
                errors[item] = 'missing'
            elif item in ['start_at', 'end_at']:
                if not isinstance(getattr(self, item), datetime):
                    errors[item] = 'invalid'
        if ('start_at' not in errors) and ('end_at' not in errors):
            if self.end_at < self.start_at:
                errors['end_at'] = 'invalid'
        return errors


class Article(ndb.Model):
    title = ndb.StringProperty(required=True, default="")
    author = ndb.StringProperty(required=True, default="")
    description = ndb.StringProperty(required=True, default="")
    body = ndb.TextProperty()
    unit = ndb.KeyProperty(required=True, kind=Unit)
    event = ndb.KeyProperty(kind=Event)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def query_unit(cls, unit_key):
        keys = [unit_key]
        while unit_key.parent():
            unit_key = unit_key.parent()
            keys += unit_key
        return cls.query_units(keys)

    @classmethod
    def query_units(cls, keys):
        return cls.query(cls.unit.IN(keys)).order(-cls.created_at)

    def from_multidict(self, mdict):
        if strexist(mdict.get('unit')):
            self.unit = ndb.Key(urlsafe=mdict.get('unit'))
        if strexist(mdict.get('event')):
            self.event = ndb.Key(urlsafe=mdict.get('event'))
        for item in ['title', 'author', 'description', 'body']:
            if strexist(mdict.get(item)):
                setattr(self, item, mdict.get(item))

    def validate(self):
        errors = {}
        for item in ['unit', 'title', 'author', 'description', 'body']:
            if not getattr(self, item):
                errors[item] = 'missing'
        return errors


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
