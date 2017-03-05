# coding: utf8

import sys
import signal
import logging

from shadowsocks import daemon, eventloop, tcprelay, udprelay, asyncdns

from .config import Config


def control(action, server):
    server_config = Config.servers.get(server)
    config = Config.application.copy()
    config.update(server_config)
    if action not in ('start', 'stop', 'restart'):
        raise BadAction('Bad Action for shadowsocks: ' + action)
    config['daemon'] = action
    daemon.daemon_exec(config)

    logger = logging.getLogger('shadowsocks.local')
    logger.info("starting local at {}:{}".format(
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


class BadAction(ValueError):
    pass
