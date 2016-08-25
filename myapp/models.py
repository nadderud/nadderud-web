#!/usr/bin/env python

from datetime import timedelta
from google.appengine.ext import ndb

from myapp import dateparser


def semester_from_date(start_at):
    semester = 'v'
    if start_at.timetuple().tm_yday > 222:  # 10 Aug
        semester = 'h'
    return semester + start_at.strftime('%y')


def convert_by_name(value_name, value):
    if value_name in ['start_at', 'end_at']:
        return dateparser.multiparse(value)
    elif value_name in ['unit', 'event']:
        return ndb.Key(urlsafe=value)
    else:
        return value


def strexist(str):
    return isinstance(str, unicode)


def assign_if_present(target, value_name, value):
    if strexist(value):
        setattr(target, value_name, convert_by_name(value_name, value))


class Assignable(ndb.Model):
    @classmethod
    def query_unit(cls, unit_key):
        keys = [unit_key]
        while unit_key.parent():
            unit_key = unit_key.parent()
            keys += unit_key
        return cls.query_units(keys)


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


class Event(Assignable):
    name = ndb.StringProperty(required=True, default="")
    location = ndb.StringProperty(required=True, default="")
    start_at = ndb.DateTimeProperty(required=True)
    end_at = ndb.DateTimeProperty(required=True)
    unit = ndb.KeyProperty(required=True, kind=Unit)
    responsibility = ndb.StringProperty(required=True, default="")
    remark = ndb.StringProperty(required=True, default="")
    semester = ndb.ComputedProperty(lambda self:
                                    semester_from_date(self.start_at))

    @property
    def positive_duration(self):
        if self.start_at and self.end_at:
            return self.start_at <= self.end_at
        else:
            return False

    @classmethod
    def query_units(cls, keys):
        return cls.query(cls.unit.IN(keys)).order(cls.start_at, cls.end_at)

    def from_multidict(self, mdict):
        for item in ['unit', 'event', 'start_at', 'end_at', 'name', 'location',
                     'responsibility', 'remark']:
            assign_if_present(self, item, mdict.get(item))
        if self.start_at and strexist(mdict.get('duration')):
            self.end_at = self.start_at + \
                timedelta(hours=float(mdict.get('duration')))

    def validate(self):
        errors = {}
        for item in ['unit', 'name', 'location', 'start_at', 'end_at']:
            if not getattr(self, item):
                errors[item] = 'missing'
        if not self.positive_duration:
            errors['end_at'] = 'invalid'
        return errors


class Article(Assignable):
    title = ndb.StringProperty(required=True, default="")
    author = ndb.StringProperty(required=True, default="")
    description = ndb.StringProperty(required=True, default="")
    body = ndb.TextProperty()
    unit = ndb.KeyProperty(required=True, kind=Unit)
    event = ndb.KeyProperty(kind=Event)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def query_units(cls, keys):
        return cls.query(cls.unit.IN(keys)).order(-cls.created_at)

    def from_multidict(self, mdict):
        for item in ['unit', 'event', 'title', 'author', 'description',
                     'body']:
            assign_if_present(self, item, mdict.get(item))

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
