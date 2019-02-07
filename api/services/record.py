#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.api import datastore_errors


class InvalidRecord(Exception):
    pass


class Record(ndb.Model):
    settable = []
    filterable = []
    sort = None

    @classmethod
    def all(cls, req):
        q = cls.query()
        if req.get_param("enhet") and "enhet" in cls.filterable:
            enhet, patrulje = (req.get_param(
                "enhet").split("/", 2) + [None])[:2]
            q = q.filter(cls.enhet.IN(["", enhet]))
            if patrulje:
                q = q.filter(cls.patrulje.IN(["", patrulje]))

        if req.get_param("semester") and "semester" in cls.filterable:
            raw_semester = req.get_param("semester")
            try:
                year = 2000 + int(raw_semester[1:])
                semester_break_date = datetime(year, 8, 10)
                if raw_semester[:1] == "v":
                    q = q.filter(cls.start >= datetime(year, 1, 1),
                                 cls.start < semester_break_date)
                else:
                    q = q.filter(cls.start >= semester_break_date,
                                 cls.start < datetime(year + 1, 1, 1))
            except:
                pass
        elif "semester" in cls.filterable:  # standard filter
            q = q.filter(cls.slutt >= datetime.today()).order(cls.slutt)

        return [i.to_dict_with_id() for i in q.order(*cls.sort).fetch()]

    @classmethod
    def create(cls, values, str_id=None):
        item = cls()
        if str_id:
            item.key = cls.key_from_str(str_id)
        item.populate_with(values)
        key = item.put()
        return dict(id=key.id())

    @classmethod
    def get(cls, str_id):
        item = cls.key_from_str(str_id).get()
        return item.to_dict_with_id() if item else None

    @classmethod
    def update(cls, values, str_id):
        item = cls.key_from_str(str_id).get()
        item.populate_with(values)
        item.put()

    @classmethod
    def delete(cls, str_id):
        cls.key_from_str(str_id).delete()

    @classmethod
    def key_from_str(cls, str_id):
        return ndb.Key(cls, int(str_id))

    def populate_with(self, dict):
        self._errors = {}

        for attr in self.settable:
            if attr in dict:
                try:
                    setattr(self, attr, dict.get(attr))
                except datastore_errors.BadValueError as err:
                    self._errors[attr] = str(err)
            if self._properties[attr]._required == True and getattr(self, attr) == None:
                self._errors[attr] = u"må oppgis"

        if len(self._errors) > 0:
            raise InvalidRecord(self._errors)

    def to_dict_with_id(self):
        return dict(self.to_dict(), **dict(id=self.key.id()))
