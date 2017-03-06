# -*- coding: utf-8 -*-
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

from gi.repository import Gtk, Gio # noqa

from shadowsocks_pygtk.config import Config  # noqa
try:
    from shadowsocks.cryptor import method_supported  # noqa
except ImportError as e:
    from shadowsocks.encrypt import method_supported  # noqa


class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        self.set_default_size(490, 330)

        self.set_titlebar(self.get_header_bar())

        action = Gio.SimpleAction.new('add', None)
        action.connect("activate", self.on_add_clicked)
        self.add_action(action)

        bodybox = Gtk.Box()
        self.add(bodybox)
        bodybox.pack_start(self.create_server_lists(), True, True, 0)

        bodybox.pack_start(self.create_config_form(), True, True, 0)

    def get_header_bar(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)

        menu_button = Gtk.MenuButton()
        header_bar.pack_end(menu_button)

        self.connect_toggle = Gtk.ToggleButton('Connect')
        self.connect_toggle.set_action_name('app.connect')
        header_bar.pack_start(self.connect_toggle)
        # start
        add_button = Gtk.Button()
        add_icon = Gio.ThemedIcon(name='gtk-add')
        add_image = Gtk.Image.new_from_gicon(add_icon, Gtk.IconSize.BUTTON)
        add_button.set_action_name('win.add')
        add_button.add(add_image)
        header_bar.pack_end(add_button)

        return header_bar

    def create_config_form(self):
        formbox = Gtk.Fixed()
        formbox.set_margin_top(10)
        address_label = Gtk.Label('服务器地址')
        formbox.put(address_label, 20, 15)
        self.server_address = Gtk.Entry()
        self.server_address.set_size_request(200, -1)
        self.server_address.set_editable(False)
        formbox.put(self.server_address, 105, 10)
        port_label = Gtk.Label('服务器端口')
        formbox.put(port_label, 20, 55)
        self.server_port = Gtk.Entry()
        self.server_port.set_size_request(200, -1)
        self.server_port.set_input_purpose(Gtk.InputPurpose.DIGITS)
        formbox.put(self.server_port, 105, 50)
        passwd_label = Gtk.Label('密码')
        formbox.put(passwd_label, 20, 95)
        self.password = Gtk.Entry()
        self.password.set_size_request(200, -1)
        self.password.set_input_purpose(Gtk.InputPurpose.PASSWORD)
        formbox.put(self.password, 105, 90)
        crypt_label = Gtk.Label('加密算法')
        formbox.put(crypt_label, 20, 135)
        self.get_crypt_methods()
        self.crypt_method = Gtk.ComboBox.new_with_model(
            self.crypt_model
        )
        renderer_text = Gtk.CellRendererText()
        self.crypt_method.pack_start(renderer_text, True)
        self.crypt_method.add_attribute(renderer_text, "text", 0)
        self.crypt_method.set_size_request(200, -1)
        formbox.put(self.crypt_method, 105, 130)
        name_label = Gtk.Label('配置名称')
        formbox.put(name_label, 20, 175)
        self.config_name = Gtk.Entry()
        self.config_name.set_size_request(200, -1)
        formbox.put(self.config_name, 105, 170)

        save_button = Gtk.Button('保存')
        save_button.set_action_name('app.save')
        delete_button = Gtk.Button('delete')
        delete_button.connect('clicked', self.on_delete_clicked)
        formbox.put(save_button, 248, 220)
        formbox.put(delete_button, 105, 220)

        return formbox

    def get_saved_servers(self):
        self.servers_model = Gtk.ListStore(str)
        for server in Config.servers:
            self.servers_model.append([server])

    def create_server_lists(self):
        self.get_saved_servers()

        self.server_view = Gtk.TreeView(model=self.servers_model)
        self.server_view.set_headers_visible(False)
        renderer = Gtk.CellRendererText()
        columns = Gtk.TreeViewColumn('服务器列表', renderer, text=0)
        self.server_view.append_column(columns)

        self.server_view.get_selection().connect(
            'changed',
            self.on_server_selected
        )

        swindow = Gtk.ScrolledWindow()
        swindow.set_size_request(150, -1)
        swindow.set_margin_top(10)
        swindow.set_margin_left(4)
        swindow.set_margin_bottom(5)

        swindow.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        swindow.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )

        swindow.add(self.server_view)

        return swindow

    def on_add_clicked(self, action, parameter):
        idx = self.servers_model.append(['new server'])
        self.server_view.get_selection().select_iter(idx)
        self.server_address.set_editable(True)

    def on_delete_clicked(self, btn):
        (model, idx) = self.server_view.get_selection().get_selected()
        if not idx:
            return True
        if model[idx][0] in Config.servers:
            return True
        row = model[idx].get_previous()
        model.remove(idx)
        if row:
            return self.server_view.get_selection().select_iter(row.iter)
        return True

    def on_server_selected(self, selection):
        (model, _iter) = selection.get_selected()
        name = model[_iter][0]
        cfg = Config.servers.get(name, None)
        if not cfg:
            self.server_address.set_text('')
            self.server_port.set_text('')
            self.password.set_text('')
            self.config_name.set_text('')
            return True
        self.server_address.set_text(cfg.server)
        self.server_port.set_text(str(cfg.server_port))
        self.password.set_text(cfg.password)
        self.config_name.set_text(name)
        self.crypt_method.set_active(
            list(method_supported.keys()).index(cfg.method)
        )

    def get_crypt_methods(self):
        self.crypt_model = Gtk.ListStore(str)
        for method in method_supported:
            self.crypt_model.append([method])
