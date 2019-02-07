#!/usr/bin/env python
# coding: utf-8

from api.services import settings
import markdown2
import base64
import json
from google.appengine.api import urlfetch


class Email(object):
    _errors = []

    def __init__(self, subject, raw, recipients):
        self._subject = subject
        self._raw = raw
        self._recipients = set(filter(None, recipients))

    def html_body(self):
        return markdown2.markdown(self._raw)

    def text_body(self):
        return self._raw

    def subject(self):
        return self._subject

    def _validate(self):
        self._errors = []

        if not self._recipients:
            self._errors.append("Du har ikke valgt noen mottakere.")
        if not self._subject:
            self._errors.append("Du har ikke skrevet noe emne.")
        if not self._raw:
            self._errors.append("Du har ikke skrevet noen melding.")

        if self._errors:
            return False
        return True

    def errors(self):
        return self._errors

    def recipients(self):
        return len(self._recipients)

    def send(self):
        if not self._validate():
            return False

        MAILJET_API_KEY = settings.get('MJ_APIKEY_PUBLIC')
        MAILJET_API_SECRET = settings.get('MJ_APIKEY_PRIVATE')

        payload = {
            'FromEmail': 'post@nadderud.no',
            'FromName': 'Nadderud speidergruppe',
            'Subject': self.subject(),
            'Text-part': self.text_body(),
            'Html-part': self.html_body(),
            'Recipients': list(map(lambda email: {'Email': email}, self._recipients))
        }

        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Basic %s' % base64.b64encode(MAILJET_API_KEY + ':' + MAILJET_API_SECRET)}

        result = urlfetch.fetch(
            url='https://api.mailjet.com/v3/send',
            payload=json.dumps(payload),
            method=urlfetch.POST,
            headers=headers,
            validate_certificate=True)

        if result.status_code == 200:
            return True

        self._errors.append("Det oppsto en uventet feil da vi prøvde å sende.")
        return False
