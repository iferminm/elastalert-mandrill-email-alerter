import logging
import mandrill

from elastalert.alerts import Alerter, BasicMatchString


class MandrillAlerter(Alerter):
    required_options = frozenset(['mandrill_api_key', 'email'])

    def __init__(self, *args):
        super(MandrillAlerter, self).__init__(*args)

        self.mandrill_api_key = self.rule.get('mandrill_api_key')
        self.mandrill_client = mandrill.Mandrill(self.mandrill_api_key)

        if isinstance(self.rule['email'], str):
            self.rule['email'] = [self.rule['email']]

        self.to = [{'email': email, 'name': 'Admin', 'type': 'to'} for email in self.rule['email']]

    def alert(self, matches):
        body = ''
        for match in matches:
            body += str(BasicMatchString(self.rule, match))
            # Separate text of aggregated alerts with dashes
            if len(matches) > 1:
                body += '\n----------------------------------------\n'

        message = {
            'to': self.to,
            'from_email': 'admin@admin.com',
            'from_name': 'DBZ Notifications',
            'text': body
        }

        status = self.mandrill_client.messages.send(message=message, async=False)
        print status

        logging.info("Sent email to %s" % (self.rule['email']))

    def create_default_title(self, matches):
        subject = 'ElastAlert: %s' % (self.rule['name'])

        # If the rule has a query_key, add that value plus timestamp to subject
        if 'query_key' in self.rule:
            qk = matches[0].get(self.rule['query_key'])
            if qk:
                subject += ' - %s' % (qk)

        return subject

    def get_info(self):
        return {'type': 'email',
                'recipients': self.rule['email']}

