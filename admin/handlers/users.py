from api.services import auth

from website import SiteHandler


class UserAdmin(SiteHandler):
    def get(self):
        if self.authorize('adminUsers', '*/*'):
            self.render('admin/users',
                        {'grants': auth.grants(), 'roles': auth.ROLES})

    def post(self):
        if self.authorize('adminUsers', '*/*'):
            if self.request.POST.get('verb') == 'delete':
                auth.revoke_grant(self.request.get('key'))

            elif self.request.POST.get('verb') == 'post':
                role = self.request.POST.get('role')
                scope = self.request.POST.get('scope').lower()
                user = auth.get_user(self.request.POST.get('user'))
                if user and role and scope:
                    user.grant(role, scope)

            self.redirect('/admin/brukere/')
