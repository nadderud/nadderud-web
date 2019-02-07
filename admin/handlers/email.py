from website import SiteHandler
from api.services import members
from api.services.messaging import email


class Email(SiteHandler):
    def get(self):
        if self.authorize('sendEmail', '*/*'):
            byPatrol = members.byPatrol(members.fetchFromApi())

            template_values = {
                'units': sorted(byPatrol),
                'members': byPatrol
            }
            self.render('admin/email', template_values)

    def post(self):
        if self.authorize('sendEmail', '*/*'):
            msg = email.Email(
                self.request.POST['subject'],
                self.request.POST['message'],
                ','.join(self.request.POST.getall('email')).lower().split(',')
            )

            msg.send()

            self.render('admin/email_sent', {
                'errors': msg.errors(),
                'subject': msg.subject(),
                'html_body': msg.html_body(),
                'emails': msg.recipients()
            })
