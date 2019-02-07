from google.appengine.api import users
from google.appengine.ext import ndb


def get_current_user():
    return User.current()


def is_current_user_admin():
    return users.is_current_user_admin()


def get_user(username):
    return User.from_email(username)


def grants():
    return Grant.query().order(Grant.key).fetch()


def revoke_grant(urlsafe_key=None):
    """Revokes an urlsafe-encoded grant key."""
    if urlsafe_key:
        grant_key = ndb.Key(urlsafe=urlsafe_key)
        if grant_key.kind() == 'Grant':
            grant_key.delete()


def logout_url(path='/'):
    return users.create_logout_url(path)


class User(ndb.Model):
    """User stores an user."""

    user = ndb.UserProperty(required=True)
    email = ndb.ComputedProperty(lambda self: self.user.email())
    nickname = ndb.ComputedProperty(lambda self: self.user.nickname())

    def id(self):
        return self.key.id()

    def scopes(self, role):
        """Returns an array of scopes for a given role."""
        scopes = []
        query = Grant.query(ancestor=self._role_key(role))

        for key in query.iter(keys_only=True):
            scopes.append(key.id())

        return scopes

    def can(self, role, scope):
        """Returns a boolean indicating whether the user has access to a given role and scope. If 
        current user is admin, this is always true."""
        if is_current_user_admin():
            return True

        return self._scope_key(role, scope).get() is not None

    def grant(self, role, scope):
        """Grant access to the role and scope for this user."""
        grant = Grant(email=self.email, id=scope, parent=self._role_key(role))
        grant.put()

    def revoke(self, role, scope):
        """Revoke access for the role and scope for this user."""
        self._scope_key(role, scope).delete()

    def _role_key(self, role):
        return ndb.Key(User, self.id(), 'Role', role)

    def _scope_key(self, role, scope):
        return ndb.Key('User', self.id(), 'Role', role, 'Grant', scope)

    @classmethod
    def current(cls):
        user = users.get_current_user()
        if user is None:
            return None
        return cls(id=user.user_id(), user=user)

    @classmethod
    def from_email(cls, email):
        key = cls(user=users.User(email)).put()
        obj = key.get(use_cache=False, use_memcache=False)
        key.delete()
        new_obj = cls(id=obj.user.user_id(), user=obj.user)
        new_obj.put()
        return new_obj


class Grant(ndb.Model):
    email = ndb.StringProperty(required=True)
