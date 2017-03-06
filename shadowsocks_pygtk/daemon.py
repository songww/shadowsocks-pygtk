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
import sys
import time
import errno
import signal
import logging

from gi.repository import Gio, GLib
from shadowsocks import daemon, eventloop, tcprelay, udprelay, asyncdns

from shadowsocks_pygtk.config import Config


class Daemon:
    logger = logging.getLogger('shadowsocks.local')
    config = G

    @classmethod
    def get_pid(cls, pid_file):
        try:
            with open(pid_file) as f:
                buf = f.read()
                if not buf:
                    raise Stopped('sslocal is not running')
        except IOError as e:
            cls.logger.exception(e)
            if e.errno == errno.ENOENT:
                raise Stopped('sslocal is not running')
            raise Stopped(e)
        return int(buf)

    @classmethod
    def start(cls, pid_file, log_file):
        Gio.Subprocess('/usr/local/bin/sslocal -c ' + Config.app)


    @classmethod
    def stop(cls, pid_file):
        pid = cls.get_pid(pid_file)
        if pid > 1:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    raise Stopped('sslocal is not running')
                raise Stopped(e)
        else:
            raise BadPid('Unknown pid: {}'.format(pid))

        for i in range(0, 200):
            try:
                os.kill(pid, 0)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    break
            time.sleep(0.05)
        else:
            raise Timeout('timed out when stopping pid {}'.format(pid))
        cls.logger.info('stopped')
        os.unlink(pid_file)

    @classmethod
    def restart(cls, pid_file, log_file):
        try:
            cls.stop(pid_file)
        except Exception as e:
            cls.logger.exception(e)
        cls.start(pid_file)

    @classmethod
    def control(cls, _signal, server):
        server_config = Config.servers.get(server)
        config = Config.application.copy()
        config.update(server_config)
        if _signal == 'start':
            cls.start(config['pid_file'], config['log_file'])
            cls.serve(config)
        elif _signal == 'stop':
            cls.stop(config['pid_file'])
        elif _signal == 'restart':
            cls.restart(config['pid_file'], config['log_file'])
            cls.serve(config)
        else:
            raise BadSignal('Bad signal for sslocal: ' + _signal)
        return

    @classmethod
    def serve(cls, config):
        cls.logger.info("starting local at {}:{}".format(
            config['local_address'],
            config['local_port']
        ))

        dns_resolver = asyncdns.DNSResolver()
        tcp_server = tcprelay.TCPRelay(config, dns_resolver, True)
        udp_server = udprelay.UDPRelay(config, dns_resolver, True)
        loop = eventloop.EventLoop()
        dns_resolver.add_to_loop(loop)
        tcp_server.add_to_loop(loop)
        udp_server.add_to_loop(loop)

        def handler(signum, _):
            logging.warn('received SIGQUIT, doing graceful shutting down..')
            tcp_server.close(next_tick=True)
            udp_server.close(next_tick=True)
        signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), handler)

        def int_handler(signum, _):
            sys.exit(1)
        signal.signal(signal.SIGINT, int_handler)

        daemon.set_user(config.get('user', None))
        loop.run()


class BadSignal(ValueError):
    pass


class Stopped(Exception):
    pass


class BadPid(Exception):
    pass


class Timeout(Exception):
    pass
