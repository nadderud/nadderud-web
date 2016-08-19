#!/usr/bin/env python

import os

import jinja2
import webapp2

from datetime import timedelta

from google.appengine.ext import ndb
from myapp.models import Unit, Event
from myapp.dateparser import parse_datetime

MY_KEYS = [
    Unit.get_key_from_string(''),
    Unit.get_key_from_string('flokken'),
    Unit.get_key_from_string('troppen'),
    Unit.get_key_from_string('troppen/ulv'),
]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates/'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, manager!')


class EventHandler(webapp2.RequestHandler):
    def upset_event(self, event):
        """Sets request variables to event."""
        errors = {}

        if isinstance(self.request.POST.get('unit'), unicode):
            event.unit = ndb.Key(urlsafe=self.request.POST.get('unit'))
        if not event.unit:
            errors['unit'] = 'missing'

        for item in ['responsibility', 'remark']:
            if isinstance(self.request.POST.get(item), unicode):
                setattr(event, item, self.request.POST.get(item).strip())

        for item in ['name', 'location']:
            if isinstance(self.request.POST.get(item), unicode):
                setattr(event, item, self.request.POST.get(item).strip())
            if not getattr(event, item):
                errors[item] = 'missing'

        if isinstance(self.request.POST.get('start_at'), unicode):
            event.start_at = parse_datetime(self.request.POST.get('start_at'))

        if not event.start_at:
            errors['start_at'] = 'missing'
        else:
            if isinstance(self.request.POST.get('duration'), unicode):
                event.end_at = event.start_at + \
                    timedelta(hours=float(self.request.POST.get('duration')))
            elif isinstance(self.request.POST.get('end_at'), unicode):
                event.end_at = parse_datetime(self.request.POST.get('end_at'))

            if not event.end_at:
                errors['end_at'] = 'missing'
            elif event.end_at < event.start_at:
                errors['end_at'] = 'invalid'

        return event, errors

    def get(self, eventId):
        self.response.headers['Content-Type'] = 'text/html'
        if eventId:  # edit
            template_values = {
                'title': 'Rediger hendelse',
                'event':  Event.get_by_id(int(eventId)),
                }
            if not template_values['event']:
                self.abort(404)
                return
        else:
            template_values = {
                'title': 'Rediger terminliste',
                'events': Event.query_units(MY_KEYS).fetch(100)
                }
        template_values['units'] = MY_KEYS
        template = JINJA_ENVIRONMENT.get_template('events.html')
        self.response.write(template.render(template_values))

    def post(self, eventId):
        self.response.headers['Content-Type'] = 'text/plain'
        event = Event()
        if eventId:
            event = Event.get_by_id(int(eventId))
            if not event:
                self.abort(404)
                return

            if self.request.POST.get('commit') == 'delete':
                event.key.delete()
                self.redirect('./')
                return

        event, errors = self.upset_event(event)

        if len(errors) > 0:
            self.response.write(errors)
        else:
            event.put()
            self.response.write('Success!')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/terminliste/([0-9]*)', EventHandler)
], debug=True)
