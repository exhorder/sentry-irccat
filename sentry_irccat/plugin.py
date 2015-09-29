from __future__ import absolute_import

import socket
import sentry_irccat

from django import forms
from sentry.plugins.bases.notify import (
    NotificationPlugin, NotificationConfigurationForm
)


class IRCCatConfigurationForm(NotificationConfigurationForm):
    host = forms.CharField(
        label='Host', required=False, help_text='irccat host')
    port = forms.IntegerField(
        label='Port', required=False, help_text='irccat port')
    channel = forms.CharField(
        label='Channel', required=False, help_text='channel')


class IRCCatMessage(NotificationPlugin):
    title = 'IRCCat'
    conf_key = 'irccat'
    slug = 'irccat'
    version = sentry_irccat.VERSION
    author = 'Russ Garrett'
    author_url = 'http://www.github.com/russss'
    project_conf_form = IRCCatConfigurationForm

    def is_configured(self, project):
        return all(
            self.get_option(k, project)
            for k in ('host', 'port', 'channel')
        )

    def notify(self, notification):
        event = notification.event
        group = event.group
        link = group.get_absolute_url()
        message = '[sentry %s] %s (%s)' % (
            event.server_name, event.message, link
        )
        self.send_payload(event.project, message)

    def send_payload(self, project, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((
            self.get_option('host', project),
            self.get_option('port', project)
        ))
        msg = "%s %s\r\n" % (self.get_option('channel', project), message)
        sock.send(msg)
        sock.close()
