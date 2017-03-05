# coding: utf8

import gi

from gi.repository import Gio  # noqa
from gi.repository import GLib  # noqa


class SystemProxy:
    schema = 'org.gnome.system.proxy'

    def __init__(self):
        self.gsetting = Gio.Settings(schema=self.schema)
        self.ignore_hosts = ['localhost', '127.0.0.0/8', '::1']

    def set_ignore_hosts(self, *hosts):
        self.ignore_hosts = hosts

    def apply_ignore_hosts(self):
        self.gsetting.set_value(
            'ignore-hosts',
            GLib.Variant('as', self.ignore_hosts)
        )

    def auto_config(self, pac):
        self.gsetting.set_value('use-same-proxy', GLib.Variant('b', True))
        self.gsetting.set_value('mode', GLib.Variant('s', 'auto'))
        self.gsetting.set_value('autoconfig-url', GLib.Variant('s', pac))
        return True

    def by_socks(self, host, port):
        self.gsetting.set_value('mode', GLib.Variant('s', 'manual'))
        socks = self.gsetting.get_child('socks')
        socks.set_value('host', GLib.Variant('s', host))
        socks.set_value('port', GLib.Variant('i', port))
        self.apply_ignore_hosts()
        return True
