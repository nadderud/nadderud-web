import test

from api.services import settings


class SettingsTestCase(test.TestCase):

    def testUnknownSetting(self):
        with self.assertRaises(Exception):
            settings.get("foo")
        # Repeat to ensure that NOT_SET_VALUE is treated as not set.
        with self.assertRaises(Exception):
            settings.get("foo")

    def testKnownSetting(self):
        setting = settings.Settings(id="foo", value="bar")
        setting.put()
        self.assertEqual(settings.get("foo"), "bar")
