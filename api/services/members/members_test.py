import test

from api.services import members, auth


class MembersTestCase(test.TestCase):

    FAKE_DATA = {
        "123": {"navn": "Test Person", "enhet": "Troppen", "patrulje": "Fisk"},
        "234": {"navn": "Test Person 2", "enhet": "Troppen", "patrulje": "Fugl"},
        "345": {"navn": "Test Person 3", "enhet": "Flokken", "patrulje": "Fisk"},
    }

    def setUpFakeData(self):
        self.memcacheAdd(
            "https://min.speiding.no/api/group/memberlist", self.FAKE_DATA)

    def testMembers(self):
        self.setUpFakeData()
        self.assertEqual(members.fetchFromApi(), {})
        self.loginUser()
        self.assertEqual(members.fetchFromApi(), {})
        user = auth.get_current_user()
        user.grant("members", "*/*")
        self.assertEqual(members.fetchFromApi(), self.FAKE_DATA)
        user.revoke("members", "*/*")
        user.grant("members", "Troppen/*")
        self.assertEqual(len(members.fetchFromApi()), 2)
