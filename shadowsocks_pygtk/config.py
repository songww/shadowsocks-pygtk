# -*- coding: utf-8 -*-

import os

import json

from gi.repository import GLib # noqa


class ConfigItem(dict):

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        raise AttributeError(
            "'ConfigItem' object has no attribute '" + attr + "'"
        )

    def __setattr__(self, attr, value):
        self[attr] = value

    def dumps(self):
        return json.dumps(self, indent=2)


class Configure(ConfigItem):
    path = os.path.join(GLib.get_user_config_dir(), GLib.get_application_name())
    servers = ConfigItem()
    app = os.path.join(path, GLib.get_application_name() + '.json')

    def get_server_path(self, server_name):
        return os.path.join(self.path, 'servers', server_name)

    def save_server(self, server_name):
        filename = self.get_server_path(server_name + '.json')
        content = self.servers[server_name]
        return self._save(filename, content)

    def save_application(self):
        return self._save(self.app, self.application)

    def _save(self, filename, config):
        return GLib.file_set_contents(filename, config.dumps().encode('utf8'))

    def load_configures(self, path=None):
        if path:
            self.path = path
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        if not os.path.isfile(self.app):
            self._save(self.app, self.default())
        self.application = self._load(self.app)
        servers_path = os.path.join(self.path, 'servers')
        if not os.path.isdir(servers_path):
            os.mkdir(servers_path)
        for filename in os.listdir(servers_path):
            if filename.endswith('.json'):
                name = filename.rsplit('.json', 1)[0]
                self.servers[name] = self._load(self.get_server_path(filename))

    def _load(self, filename):
        _, content = GLib.file_get_contents(filename)
        return ConfigItem(json.loads(content.decode('utf8')))

    def default(self):
        d = ConfigItem(
            auto_connect=True,
            reconnect=True,
            local_port=1080,
            local_address='127.0.0.1',
            verbose=3,
            one_time_auth=True,
            timeout=300,
            fast_open=True,
            workers=1,
            manager_address='127.0.0.1',
            user=GLib.get_user_name(),
            forbidden_ip=[],
            daemon='daemon',
            prefer_ipv6=False
        )
        d['pid-file'] = os.path.join(
            GLib.get_user_runtime_dir(),
            GLib.get_application_name() + '.pid'
        )
        d['log-file'] = os.path.join(
            GLib.get_user_runtime_dir(),
            GLib.get_application_name() + '.log'
        )
        return d

Config = Configure()
try:
    Config.load_configures()
except Exception as e:
    print(e)
