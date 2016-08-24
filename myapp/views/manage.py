#!/usr/bin/env python

import webapp2

from myapp.models import Unit, Event, Article
from myapp.views import JINJA_ENVIRONMENT

MY_KEYS = [
    Unit.get_key_from_string(''),
    Unit.get_key_from_string('flokken'),
    Unit.get_key_from_string('troppen'),
    Unit.get_key_from_string('troppen/ulv'),
]


class BaseHandler(webapp2.RequestHandler):
    def can_i_edit(self, instance):
        if not instance:
            self.abort(404)
            return
        elif getattr(instance, 'unit') not in MY_KEYS:
            self.abort(403)
            return

    def put_success(self, instance, target):
        self.response.headers['Content-Type'] = 'text/plain'
        errors = instance.validate()
        if len(errors) > 0:
            self.response.write(errors)
        else:
            instance.put()
            self.response.write('Success!')
            self.redirect(target)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, manager!')


class EventHandler(BaseHandler):
    def get(self, eventId):
        self.response.headers['Content-Type'] = 'text/html'
        if eventId:  # edit
            template_values = {
                'title': 'Rediger hendelse',
                'event':  Event.get_by_id(int(eventId)),
                }
            self.can_i_edit(template_values['event'])
        else:
            template_values = {
                'title': 'Rediger terminliste',
                'events': Event.query_units(MY_KEYS).fetch(100)
                }
        template_values['units'] = MY_KEYS
        template = JINJA_ENVIRONMENT.get_template('events.html')
        self.response.write(template.render(template_values))

    def post(self, eventId):
        event = Event()
        if eventId:
            event = Event.get_by_id(int(eventId))
            self.can_i_edit(event)

            if self.request.POST.get('commit') == 'delete':
                event.key.delete()
                self.redirect('./')
                return

        event.from_multidict(self.request.POST)
        self.put_success(event, '/terminliste/')


class ArticleHandler(BaseHandler):
    def get(self, articleId):
        self.response.headers['Content-Type'] = 'text/html'
        if articleId:  # edit
            template_values = {
                'title': 'Rediger artikkel',
                'article':  Article.get_by_id(int(articleId)),
                }
            self.can_i_edit(template_values['article'])
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
            self.can_i_edit(article)

            if self.request.POST.get('commit') == 'delete':
                article.key.delete()
                self.redirect('./')
                return

        article.from_multidict(self.request.POST)
        self.put_success(article, '/artikler/')


class ImageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Not implemented!')

    def post(self, articleId):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Not implemented!')
