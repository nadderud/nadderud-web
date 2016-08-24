#!/usr/bin/env python

import os

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/../templates/'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, Admin!')
