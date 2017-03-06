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

import os
import logging

from gi.repository import GLib

from shadowsocks_pygtk.config import Config, ConfigItem

from shadowsocks import shell
from shadowsocks.local import main


class Daemon:
    logger = logging.getLogger('shadowsocks.local')
    config_file = None

    @classmethod
    def create_config(cls, config):
        if not cls.config_file:
            code, config_file = GLib.file_open_tmp('config_XXXXXX.json')
            cls.config_file = config_file
        GLib.file_set_contents(cls.config_file, config.dumps().encode('utf8'))

    @classmethod
    def _control(cls):
        pid = os.fork()
        if pid == 0:
            return main()
        else:
            return

    @classmethod
    def control(cls, _signal, server):
        server_config = Config.servers.get(server)
        config = ConfigItem(Config.application.copy())
        config.update(server_config)
        config.daemon = _signal
        shell.get_config = lambda x: config  # patch get_config
        if _signal in ('start', 'restart'):
            return cls._control()
        elif _signal == 'stop':
            re = cls._control()
            return re
        else:
            raise BadSignal('Bad signal for sslocal: ' + _signal)
        return


class BadSignal(ValueError):
    pass
