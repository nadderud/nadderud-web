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
    def authorize(self, item):
        if not item:
            self.abort(404)
            return
        elif getattr(item, 'unit') not in MY_KEYS:
            self.abort(403)
            return

    def get(self, itemId):
        if itemId:
            template_values = {
                'item':  self.klass.get_by_id(int(itemId)),
                }
            self.authorize(template_values['item'])
        else:
            template_values = {
                'items': self.klass.query_units(MY_KEYS).fetch(100)
                }
        template_values['units'] = MY_KEYS
        template = JINJA_ENVIRONMENT.get_template(self.template_file)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render(template_values))

    def post(self, itemId):
        if itemId:
            item = self.klass.get_by_id(int(itemId))
            self.authorize(item)
            if self.request.POST.get('commit') == 'delete':
                item.key.delete()
                self.redirect('./')
                return
        else:
            item = self.klass()

        item.from_multidict(self.request.POST)
        self.response.headers['Content-Type'] = 'text/plain'
        errors = item.validate()
        if len(errors) > 0:
            self.response.write(errors)
        else:
            item.put()
            self.response.write('Success!')
            self.redirect(self.collection_path)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, manager!')


class EventHandler(BaseHandler):
    collection_path = '/terminliste/'
    klass = Event
    template_file = 'events.html'


class ArticleHandler(BaseHandler):
    collection_path = '/artikler/'
    klass = Article
    template_file = 'articles.html'


class ImageHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Not implemented!')

    def post(self, articleId):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Not implemented!')
