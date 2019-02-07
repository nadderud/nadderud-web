import test

from api.services import auth


class UserTestCase(test.TestCase):

    def testUserGetCurrentIfNone(self):
        user = auth.get_current_user()
        self.assertFalse(user)

    def testUserGetCurrentIfUser(self):
        self.loginUser()
        user = auth.get_current_user()
        self.assertEqual(user.id(), '123')

    def testUserGrants(self):
        self.loginUser()
        user = auth.get_current_user()
        user.grant('sendEmail', '*/*')
        self.assertTrue(user.can('sendEmail', '*/*'))
        self.assertEqual(user.scopes('sendEmail'), ['*/*'])
        user.grant('sendEmail', 'flokken/*')
        self.assertEqual(user.scopes('sendEmail'), ['*/*', 'flokken/*'])
        user.revoke('sendEmail', '*/*')
        self.assertFalse(user.can('sendEmail', '*/*'))

    def testAdminGrant(self):
        self.loginUser(is_admin=True)
        user = auth.get_current_user()
        self.assertTrue(user.can('Foo', 'Bar'))

    def testGrants(self):
        self.assertEqual(len(auth.grants()), 0)
        user = auth.get_user('test@example.com')
        user.grant('foo', '*/*')
        user = auth.get_user('test2@example.com')
        user.grant('foo', '*/*')
        self.assertEqual(len(auth.grants()), 2)
