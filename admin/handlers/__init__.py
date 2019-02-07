from website import SiteHandler


from admin.handlers.email import Email
from admin.handlers.users import UserAdmin


class Main(SiteHandler):
    def get(self):
        self.get_user()
        self.render()


class Kick(SiteHandler):
    def get(self):
        self.redirect('/')
