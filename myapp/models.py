#!/usr/bin/env python

from google.appengine.ext import ndb


class Unit(ndb.Model):
    name = ndb.StringProperty(required=True, default="")
    active = ndb.BooleanProperty(required=True, default=True)


class Event(ndb.Model):
    name = ndb.StringProperty(required=True, default="")
    location = ndb.StringProperty(required=True, default="")
    start_at = ndb.DateTimeProperty(required=True)
    end_at = ndb.DateTimeProperty(required=True)
    responsibility = ndb.StringProperty(required=True, default="")
    remark = ndb.StringProperty(required=True, default="")


class Article(ndb.Model):
    title = ndb.StringProperty(required=True, default="")
    author = ndb.StringProperty(required=True, default="")
    description = ndb.StringProperty(required=True, default="")
    body = ndb.TextProperty()
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
