#!/usr/bin/env python3
# coding: utf8
#
# Copyright (C) 2017 songww
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
gi.require_version('GLib', '2.0')

from gi.repository import Gtk, GLib, Gio  # noqa
try:
    from shadowsocks.cryptor import method_supported  # noqa
except ImportError as e:
    from shadowsocks.encrypt import method_supported  # noqa

from shadowsocks_pygtk.window import AppWindow   # noqa
from shadowsocks_pygtk.config import ConfigItem, Config  # noqa
from shadowsocks_pygtk.daemon import Daemon  # noqa


class Shadowsocks(Gtk.Application):
    signals = {
        'connect': 'on_connection_toggled',
        'save': 'on_server_saved',
    }

    def __init__(self, **kwargs):
        super().__init__(application_id='org.gnome.ShadowsocksPygtk', **kwargs)
        GLib.set_application_name('shadowsocks')

    def do_activate(self):
        self.window = AppWindow(title='shadowsocks', application=self)
        self.window.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.create_signals()
        self.connected_server = None
        if Config.application.auto_connect and Config.application.last_server:
            Daemon.control('start', Config.application.last_server)
            self.connected_server = Config.application.last_server

    def create_signals(self):
        for signal, callback in self.signals.items():
            action = Gio.SimpleAction.new(signal, None)
            action.connect("activate", getattr(self, callback))
            self.add_action(action)

    def on_connection_toggled(self, action, parameter):
        if self.window.connect_toggle.get_active() and self.connected_server:
            try:
                return Daemon.control('stop', self.connected_server)
            except Exception:
                pass
        (model, idx) = self.window.server_view.get_selection().get_selected()
        name = model[idx][0]
        Daemon.control('start', name)
        Config.application.last_server = self.connected_server = name
        Config.save_application()
        print('x')

    def on_server_saved(self, action, parameter):
        name = self.window.config_name.get_text()
        server = self.window.server_address.get_text()
        if not name:
            name = server
        method_index = self.window.crypt_method.get_active()
        method = list(method_supported.keys())[method_index]
        Config.servers[name] = ConfigItem(
            method=method,
            server=server,
            password=self.window.password.get_text(),
            server_port=int(self.window.server_port.get_text()),
        )
        Config.save_server(name)
        if self.connected_server == name:
            Daemon.control('restart', name)
