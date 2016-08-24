#!/usr/bin/env python

import webapp2

from myapp.views import admin, manage


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

app = webapp2.WSGIApplication([
    ('/nadderud/', MainPage),
    ('/admin/', admin.MainPage),
    ('/', manage.MainPage),
    ('/terminliste/([0-9]*)', manage.EventHandler),
    ('/artikler/([0-9]*)', manage.ArticleHandler),
    ('/bilder/([0-9]*)', manage.ImageHandler),
], debug=True)
