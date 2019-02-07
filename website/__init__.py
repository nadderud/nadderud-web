#!/usr/bin/env python

import webapp2
import jinja2
import os

from api.services import auth

TEMPLATES_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'templates')


class SiteHandler(webapp2.RequestHandler):
    user = None
    logout_url = ""
    is_admin = False

    def get_user(self):
        self.user = auth.get_current_user()
        self.logout_url = auth.logout_url()
        self.is_admin = auth.is_current_user_admin()

    def authorize(self, role, scope):
        self.get_user()

        if not self.user.can(role, scope):
            self.response.write('Du har ikke tilgang til dette.')
            return False

        return True

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATES_PATH),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True)

    def render(self, filename=None, values={}):
        path = filename or self.request.path.strip('/')
        template_path = '404.html'

        for ext in ['/index.html', '.html']:
            test_path = path + ext
            if os.path.isfile(os.path.join(TEMPLATES_PATH, test_path)):
                template_path = test_path
                break

        values['user'] = self.user
        values['logout_url'] = self.logout_url
        values['is_admin'] = self.is_admin

        template = self.jinja2.get_template(template_path)
        self.response.write(template.render(values))


class StaticPage(SiteHandler):
    def get(self):
        self.render()


class FrontPage(SiteHandler):
    def get(self):
        self.render('index')


app = webapp2.WSGIApplication([
    ('/', FrontPage),
    ('/.*', StaticPage),
])
