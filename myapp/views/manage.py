#!/usr/bin/env python

import os

import jinja2
import webapp2

from datetime import timedelta

from google.appengine.ext import ndb
from myapp.models import Unit, Event, Article
from myapp.dateparser import parse_datetime

MY_KEYS = [
    Unit.get_key_from_string(''),
    Unit.get_key_from_string('flokken'),
    Unit.get_key_from_string('troppen'),
    Unit.get_key_from_string('troppen/ulv'),
]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/../templates/'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def request_setter(request, target, value_name, required, transform=None):
    if isinstance(request.get(value_name), unicode):
        value = request.get(value_name).strip()
        if transform:
            value = transform(value)
        setattr(target, value_name, value)
    if required and not getattr(target, value_name):
        return {value_name: 'missing'}
    return {}


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, manager!')


class EventHandler(webapp2.RequestHandler):
    def upset_event(self, event):
        """Sets request variables to event."""
        errors = {}

        errors.update(request_setter(self.request.POST, event, 'unit', True,
                       lambda x: ndb.Key(urlsafe=x)))

        for item, req in [
            ('responsibility', False),
            ('remark', False),
            ('name', True),
            ('location', True),
        ]:
            errors.update(request_setter(self.request.POST, event, item, req))

        for item in ['start_at', 'end_at']:
            request_setter(self.request.POST, event, item, False,
                           lambda x: parse_datetime(x))

        if not event.start_at:
            errors['start_at'] = 'missing'
        else:
            if isinstance(self.request.POST.get('duration'), unicode):
                event.end_at = event.start_at + \
                    timedelta(hours=float(self.request.POST.get('duration')))

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
            elif template_values['event'].unit not in MY_KEYS:
                self.abort(403)
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
            elif event.unit not in MY_KEYS:
                self.abort(403)
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


class ArticleHandler(webapp2.RequestHandler):
    def upset_article(self, article):
        """Sets request variables to article."""
        errors = {}

        errors.update(request_setter(self.request.POST, article, 'unit', True,
                      lambda x: ndb.Key(urlsafe=x)))

        errors.update(request_setter(self.request.POST, article, 'event',
                      False, lambda x: ndb.Key(urlsafe=x)))

        for item in ['title', 'author', 'description', 'body']:
            errors.update(request_setter(self.request.POST, article, item,
                                         True))

        return article, errors

    def get(self, articleId):
        self.response.headers['Content-Type'] = 'text/html'
        if articleId:  # edit
            template_values = {
                'title': 'Rediger artikkel',
                'article':  Article.get_by_id(int(articleId)),
                }
            if not template_values['article']:
                self.abort(404)
                return
            elif template_values['article'].unit not in MY_KEYS:
                self.abort(403)
                return
        else:
            template_values = {
                'title': 'Rediger artikler',
                'articles': Article.query_units(MY_KEYS).fetch(100)
                }
        template_values['units'] = MY_KEYS
        template = JINJA_ENVIRONMENT.get_template('articles.html')
        self.response.write(template.render(template_values))

    def post(self, articleId):
        self.response.headers['Content-Type'] = 'text/plain'
        article = Article()
        if articleId:
            article = Article.get_by_id(int(articleId))
            if not article:
                self.abort(404)
                return
            elif article.unit not in MY_KEYS:
                self.abort(403)
                return

            if self.request.POST.get('commit') == 'delete':
                article.key.delete()
                self.redirect('./')
                return

        article, errors = self.upset_article(article)

        if len(errors) > 0:
            self.response.write(errors)
        else:
            article.put()
            self.response.write('Success!')


class ImageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_values = {
            'title': 'Bilder',
            'images': []
            }
        template = JINJA_ENVIRONMENT.get_template('articles.html')
        self.response.write(template.render(template_values))

    def post(self, articleId):
        self.response.headers['Content-Type'] = 'text/plain'
        article = Article()
        if articleId:
            article = Article.get_by_id(int(articleId))
            if not article:
                self.abort(404)
                return
            elif article.unit not in MY_KEYS:
                self.abort(403)
                return

            if self.request.POST.get('commit') == 'delete':
                article.key.delete()
                self.redirect('./')
                return

        article, errors = self.upset_article(article)

        if len(errors) > 0:
            self.response.write(errors)
        else:
            article.put()
            self.response.write('Success!')
