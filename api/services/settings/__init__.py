from google.appengine.ext import ndb


def get(name):
    return Settings.get(name)


class Settings(ndb.Model):
    value = ndb.StringProperty()

    @staticmethod
    def get(name):
        NOT_SET_VALUE = 'NOT SET'
        retval = ndb.Key(Settings, name).get()
        if not retval:
            retval = Settings(id=name, value=NOT_SET_VALUE)
            retval.put()
        if retval.value == NOT_SET_VALUE:
            raise Exception(('Setting %s not found in the database. A ' +
                             'placeholder record has been created. Go to ' +
                             'the Developers Console for your app in App ' +
                             'Engine, look up the Settings record with ' +
                             'name=%s and enter its value in that record\'s ' +
                             'value field.') % (name, name))
        return retval.value
