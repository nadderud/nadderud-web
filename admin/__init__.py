#!/usr/bin/env python

import webapp2
from webapp2_extras import routes

from admin import handlers


app = webapp2.WSGIApplication([
    routes.RedirectRoute('/admin/', handlers.Main,
                         name='admin-index', strict_slash=True),
    routes.RedirectRoute('/admin/e-post/', handlers.Email,
                         name='admin-email', strict_slash=True),
    routes.RedirectRoute('/admin/brukere/', handlers.UserAdmin,
                         name='admin-users', strict_slash=True),
    ('/admin/.*', handlers.Kick)
])
